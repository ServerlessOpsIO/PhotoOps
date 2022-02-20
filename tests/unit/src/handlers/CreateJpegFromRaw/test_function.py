# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
'''Test CreateJpegFromRaw'''

import json
import os

import boto3
import jsonschema
import moto
import pytest

from boto3.dynamodb.transform import TypeSerializer
from datetime import datetime, timedelta

from common.test.aws import create_lambda_function_context

CACHE_BUCKET_NAME = 'cache-bucket'
os.environ['PHOTOOPS_S3_BUCKET'] = CACHE_BUCKET_NAME
os.environ['CROSS_ACCOUNT_IAM_ROLE_ARN'] = 'arn:aws:iam::123456789012:role/PhotoOpsAI/CrossAccountAccess'

try:
    import src.handlers.CreateJpegFromRaw.function as func
except:
    pytestmark = pytest.mark.skip


DATA_DIR = './data'
EVENT_DIR = os.path.join(DATA_DIR, 'events')
SCHEMA_DIR = os.path.join(DATA_DIR, 'schemas')
IMAGE_DIR = os.path.join(DATA_DIR, 'images')
MODEL_DIR = os.path.join(DATA_DIR, 'models')

EVENT = os.path.join(EVENT_DIR, 'CreateJpegFromRaw-event-eb.json')
EVENT_SCHEMA = os.path.join(SCHEMA_DIR, 'CreateJpegStateMachineEvent.schema.json')
RESPONSE = os.path.join(EVENT_DIR, 'CreateJpegFromRaw-output.json')
DATA_SCHEMA = os.path.join(SCHEMA_DIR, 'JpegData.schema.json')
RESPONSE_SCHEMA = os.path.join(SCHEMA_DIR, 'CreateJpegFromRawResponse.schema.json')

### AWS clients
@pytest.fixture()
def context():
    '''context object'''
    return create_lambda_function_context('CreateJpegFromRaw')

@pytest.fixture()
def aws_credentials() -> None:
    '''Mock credentials to prevent accidentally escaping our mock'''
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'


@moto.mock_sts
@pytest.fixture()
def session(aws_credentials):
    '''AWS Session client'''
    return boto3.Session()


@pytest.fixture()
def S3_CLIENT(session):
    '''S3 client'''
    with moto.mock_s3():
        yield session.client('s3')


### Images
@pytest.fixture(params=[
    'test_image_nikon.NEF',
    #'test_image_lightroom_nikon.dng',
    #'test_image_lightroom_nikon_embedded_raw.dng',
    #'test_image_lightroom_nikon.tif',
])
def image_name(request):
    '''Return an image file object'''
    return request.param


@pytest.fixture()
def image(image_name):
    '''Return an image file object'''
    return open(os.path.join(IMAGE_DIR, image_name), 'rb')


### Events
@pytest.fixture()
def event() -> dict:
    '''Return a test event'''
    with open(EVENT) as f:
        return json.load(f)


@pytest.fixture()
def event_schema() -> dict:
    '''Return an event schema'''
    with open(EVENT_SCHEMA) as f:
        return json.load(f)


@pytest.fixture()
def expected_response() -> dict:
    '''Return DDB item'''
    with open(RESPONSE) as f:
        return json.load(f)


@pytest.fixture()
def data_schema() -> dict:
    '''Return a response schema'''
    with open(DATA_SCHEMA) as f:
        return json.load(f)


@pytest.fixture()
def response_schema() -> dict:
    '''Return a response schema'''
    with open(RESPONSE_SCHEMA) as f:
        return json.load(f)


# Data validation
def test_validate_event(event: dict, event_schema: dict):
    '''Test event data against schema'''
    jsonschema.validate(event, event_schema)


def test_validate_expected_data(expected_response: dict, data_schema: dict):
    '''
    Test response data against schema

    This ensures valid data.
    '''
    jsonschema.validate(expected_response.get('Item'), data_schema)


def test_validate_expected_response(expected_response: dict, response_schema: dict):
    '''
    Test response against schema.

    This ensures a valid DDB PutItem body.
    '''
    # Note: This ensures { "Item": { "pk":"bucket", ""sk:"key", * } }
    jsonschema.validate(expected_response, response_schema)


### Tests
def test_handler(event: dict, expected_response: dict, image, S3_CLIENT, context, mocker):
    '''Call handler'''
    mocker.patch(
        'src.handlers.CreateJpegFromRaw.function._get_cross_account_s3_client',
        return_value=S3_CLIENT
    )

    mocker.patch.object(
        func,
        'S3_CLIENT',
        S3_CLIENT
    )

    # Stage file
    s3_bucket = event.get('s3_bucket', '')
    s3_object_key = event.get('s3_object_key', '')
    S3_CLIENT.create_bucket(
        Bucket=s3_bucket
    )
    S3_CLIENT.upload_fileobj(image, s3_bucket, s3_object_key)

    # Create image cache bucket
    S3_CLIENT.create_bucket(
        Bucket=CACHE_BUCKET_NAME
    )

    resp = func.handler(event, context)
    # Remove expiration since it won't match
    expiration = resp['Item'].pop('expiration_date_time')
    expected_response['Item'].pop('expiration_date_time')

    # FIXME: We should convert this
    # serialize expected response into a DDB item
    expected_ddb_items = expected_response.get('Item', {})
    expected_response['Item'] = { k: TypeSerializer().serialize(v) for k, v in expected_ddb_items.items() }

    assert resp == expected_response
    expiration = expiration.get('S')
    assert (datetime.utcnow() + timedelta(days=15)).date() == datetime.fromisoformat(expiration).date()