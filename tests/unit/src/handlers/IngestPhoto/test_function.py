# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
'''Test IngestPhoto'''

import json
import os

from datetime import datetime

import boto3
import moto
import pytest
from aws_lambda_powertools.utilities.data_classes import SNSEvent

import src.handlers.IngestPhoto.function as func

DATA_DIR = './data'
EVENT_DIR = os.path.join(DATA_DIR, 'events')
IMAGE_DIR = os.path.join(DATA_DIR, 'images')
MODEL_DIR = os.path.join(DATA_DIR, 'models')

### Events
@pytest.fixture(params=['IngestPhoto-event-put.json'])
def event(request):
    '''Return a test event'''
    with open(os.path.join(EVENT_DIR, request.param)) as f:
        return json.load(f)

@pytest.fixture(params=['IngestPhoto-event-delete.json'])
def unexpected_event(request):
    '''Return a test event'''
    with open(os.path.join(EVENT_DIR, request.param)) as f:
        return json.load(f)


@pytest.fixture()
def event_schema():
    '''Return an event schema'''
    with open(os.path.join(EVENT_DIR, 'lambda-sns-event.schema.json')) as f:
        return json.load(f)


@pytest.fixture()
def s3_notification():
    '''Return an S3 notification'''
    with open(os.path.join(EVENT_DIR, 'IngestPhoto-msg-put.json')) as f:
        return json.load(f)


@pytest.fixture()
def s3_notification_from_event(event):
    '''Return an S3 notification'''
    sns_event = SNSEvent(event)
    return json.loads(sns_event.sns_message)


@pytest.fixture()
def s3_notification_schema():
    '''Return an S3 notification'''
    with open(os.path.join(EVENT_DIR, 's3-notification.schema.json')) as f:
        return json.load(f)


### Data
@pytest.fixture()
def image_file():
    '''Image file'''
    with open(os.path.join(IMAGE_DIR, 'image_test.NEF'), 'rb') as f:
        return json.load(f)


### AWS clients
@pytest.fixture()
def aws_credentials():
    '''Mock credentials to prevent accidentally escaping our mock'''
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'


@pytest.fixture()
def S3_CLIENT(aws_credentials):
    '''S3 client'''
    with moto.mock_s3():
        yield boto3.client('s3')


@pytest.fixture()
def DDB_TABLE(aws_credentials):
    '''DDB client'''
    with moto.mock_dynamodb2():
        boto3.client('dynamodb').create_table(
            TableName='TestTable',
            KeySchema=[
                {
                    'AttributeName': 'pk',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'sk',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'pk',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'sk',
                    'AttributeType': 'S'
                }
            ]
        )
        yield boto3.resource('dynamodb').Table('TestTable')


### Helper functions.
# FIXME: How can I use my s3_client fixture by default
def _create_s3_bucket(s3_location, s3_client):
    '''Create S3 bucket'''
    s3_client.create_bucket(Bucket=s3_location.bucket)


def _put_s3_object(s3_location, s3_client, s3_body):
    '''Put S3 object'''
    s3_client.put_object(
        Bucket=s3_location.bucket,
        Key=s3_location.key
    )


### Tests
def test_handler(event, s3_notification_from_event, S3_CLIENT, DDB_TABLE, mocker):
    '''Call handler'''

    mocker.patch.object(
        func,
        'S3_CLIENT',
        S3_CLIENT
    )

    mocker.patch.object(
        func,
        'DDB_TABLE',
        DDB_TABLE
    )

    s3_location = func._get_s3_object_location(s3_notification_from_event)
    _create_s3_bucket(s3_location, S3_CLIENT)
    _put_s3_object(s3_location, S3_CLIENT, image_file)

    event_datetime = datetime.strptime(
        s3_notification_from_event['Records'][0]['eventTime'], '%Y-%m-%dT%H:%M:%S.%fZ'
    )

    resp = func.handler(event, {})
    file_name, *tmp_file_suffix = os.path.basename(s3_location.key).split('.')

    assert isinstance(resp.photo_data, func.PhotoData)
    assert resp.photo_data.file_name == file_name
    assert resp.photo_data.file_suffix == tmp_file_suffix[0]
    assert isinstance(resp.photo_data.size, int)
    assert resp.photo_data.metadata_processed is False
    assert resp.photo_data.location.bucket == s3_location.bucket
    assert resp.photo_data.location.key == s3_location.key

    assert resp.ddb.response.get('ResponseMetadata').get('HTTPStatusCode') == 200
    assert resp.ddb.item.pk == 'PHOTO#{0}#{1}'.format(s3_location.bucket, s3_location.key)
    assert resp.ddb.item.sk == 'EVENT_TIME#{0}'.format(event_datetime)



@pytest.mark.skip(reason='Need to write')
def test_handler_unexpected_event(unexpected_event):
    '''Call handler with unexpected event data'''
    pass
#    with pytest.raises( ... ):
#        resp = func.handler(unexpected_event, {})


