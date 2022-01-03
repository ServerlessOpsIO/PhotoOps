'''Test CreateJpgFromRaw'''

import json
import os

import boto3

import pytest
from aws_lambda_powertools.utilities.data_classes import EventBridgeEvent
from mypy_boto3_cloudformation import CloudFormationClient
from mypy_boto3_events import EventBridgeClient
from mypy_boto3_lambda import LambdaClient
from mypy_boto3_s3 import S3Client

STACK_NAME = os.environ.get('STACK_NAME')
FUNCTION_LOGICAL_ID = 'CreateJpegFromRaw'
EVENT_BUS_LOGICAL_ID = 'EventBus'
S3_BUCKET_NAME = 'PhotoOpsBucket'

TEST_IMAGE_BUCKET_PATH = os.environ.get('TEST_PHOTO_IMAGE_BUCKET_PATH', 'DUMMY_BUCKET').strip('/').split('/', 1)
TEST_BUCKET_NAME = TEST_IMAGE_BUCKET_PATH[0]
TEST_BUCKET_PATH = TEST_IMAGE_BUCKET_PATH[1].strip('/') if len(TEST_IMAGE_BUCKET_PATH) > 1 else ''

DATA_DIR = './data'
EVENT_DIR = os.path.join(DATA_DIR, 'events')

## AWS
@pytest.fixture()
def session():
    '''Return a boto3 session'''
    return boto3.Session()

@pytest.fixture()
def cfn_client(session) -> CloudFormationClient:
    '''Return a CFN client'''
    return session.client('cloudformation')

@pytest.fixture()
def eventbridge_client(session) -> EventBridgeClient:
    '''Return an EventBridge client'''
    return session.client('events')

@pytest.fixture()
def eventbridge_name(cfn_client) -> str:
    '''Return the EventBridge name'''
    eventbridge_name = cfn_client.describe_stack_resource(
        StackName=STACK_NAME,
        LogicalResourceId=EVENT_BUS_LOGICAL_ID
    )
    return eventbridge_name['StackResourceDetail']['PhysicalResourceId']

@pytest.fixture()
def lambda_client(session) -> LambdaClient:
    '''Return a Lambda client'''
    return session.client('lambda')

@pytest.fixture()
def lambda_function_name(cfn_client) -> str:
    '''Return the Lambda function name'''
    function_info = cfn_client.describe_stack_resource(
        StackName=STACK_NAME,
        LogicalResourceId=FUNCTION_LOGICAL_ID
    )
    return function_info['StackResourceDetail']['PhysicalResourceId']

@pytest.fixture()
def s3_client(session) -> EventBridgeClient:
    '''Return an EventBridge client'''
    return session.client('events')

@pytest.fixture()
def s3_bucket_name(cfn_client) -> str:
    '''Return the S3 bucket name'''
    s3_bucket = cfn_client.describe_stack_resource(
        StackName=STACK_NAME,
        LogicalResourceId=S3_BUCKET_NAME
    )
    return s3_bucket['StackResourceDetail']['PhysicalResourceId']


### Events
@pytest.fixture(params=[
    'test_image_nikon.NEF',
    'test_image_sony.ARW',
    'large_test_image_nikon.NEF'
    'corrupt_test_image_data_append.NEF',
    'corrupt_test_image_data_prepend.NEF'
])
def image_name(request):
    '''Return an image file name'''
    return request.param

@pytest.fixture
def base_eventbridge_event():
    '''Base EventBridge event'''
    with open(os.path.join(EVENT_DIR, 'CreateJpegFromRaw-event-eb.json')) as f:
        return json.load(f)

@pytest.fixture
def eventbridge_event(base_eventbridge_event, image_name):
    '''EventBridge event'''
    base_eventbridge_event['pk'] = '{}#{}/{}'.format(TEST_BUCKET_NAME, TEST_BUCKET_PATH, image_name)
    return base_eventbridge_event

@pytest.fixture
def expected_response(image_name):
    '''Function response'''
    file_name = 'CreateJpegFromRaw-output-{}.json'.format(image_name)
    with open(os.path.join(EVENT_DIR, file_name)) as f:
        return json.load(f)


### Tests
@pytest.mark.parametrize('image_name', ['test_image_nikon.NEF'])
def test_invoke_handler(
        eventbridge_event,
        expected_response,
        lambda_client,
        lambda_function_name,
        image_name
    ):
    '''Test invoking handler with a happy event works'''
    resp = lambda_client.invoke(
        FunctionName=lambda_function_name,
        LogType='Tail',
        Payload=json.dumps(eventbridge_event).encode('utf-8')
    )
    resp_body = json.loads(resp.pop('Payload').read().decode())

    assert resp['StatusCode'] == 200
    assert resp_body == expected_response


@pytest.mark.parametrize('image_name', ['test_image_nikon.NEF.fake'])
def test_invoke_handler_get_image_failure(
        eventbridge_event,
        lambda_client,
        lambda_function_name,
        image_name
    ):
    '''Test invoking handler with a non-fetchable image'''
    resp = lambda_client.invoke(
        FunctionName=lambda_function_name,
        LogType='Tail',
        Payload=json.dumps(eventbridge_event).encode('utf-8')
    )
    resp_body = json.loads(resp.pop('Payload').read().decode())

    assert resp['StatusCode'] == 200
    assert resp_body['errorType'] == 'ClientError'
    assert resp_body['errorMessage'] == 'An error occurred (403) when calling the HeadObject operation: Not Found'


@pytest.mark.parametrize('image_name', ['test_image_nikon.NEF'])
@pytest.mark.skip(reason='Not sure ho to cause')
def test_invoke_handler_put_image_failure(
        eventbridge_event,
        lambda_client,
        lambda_function_name,
        image_name
    ):
    '''Test invoking handler and a file that cannot be uploaded'''
    resp = lambda_client.invoke(
        FunctionName=lambda_function_name,
        LogType='Tail',
        Payload=json.dumps(eventbridge_event).encode('utf-8')
    )
    resp_body = json.loads(resp.pop('Payload').read().decode())

    assert resp['StatusCode'] == 200
    assert resp_body == {}


@pytest.mark.parametrize('image_name', ['corrupt_test_image_data_append.NEF'])
def test_invoke_handler_convert_to_jpeg_corrupt_file(
        eventbridge_event,
        lambda_client,
        lambda_function_name,
        image_name
    ):
    '''Test invoking handler and a file that cannot be converted'''
    resp = lambda_client.invoke(
        FunctionName=lambda_function_name,
        LogType='Tail',
        Payload=json.dumps(eventbridge_event).encode('utf-8')
    )
    resp_body = json.loads(resp.pop('Payload').read().decode())

    assert resp['StatusCode'] == 200
    assert resp_body == {}


@pytest.mark.parametrize('image_name', ['corrupt_test_image_data_prepend.NEF'])
def test_invoke_handler_convert_to_jpeg_corrupt_file_failure(
        eventbridge_event,
        lambda_client,
        lambda_function_name,
        image_name
    ):
    '''Test invoking handler and a file that cannot be converted'''
    resp = lambda_client.invoke(
        FunctionName=lambda_function_name,
        LogType='Tail',
        Payload=json.dumps(eventbridge_event).encode('utf-8')
    )
    resp_body = json.loads(resp.pop('Payload').read().decode())

    assert resp['StatusCode'] == 200
    assert resp_body['errorType'] == 'LibRawFileUnsupportedError'
    assert resp_body['errorMessage'] == 'Unsupported file format or not RAW file'


@pytest.mark.parametrize('image_name', ['test_image_sony.ARW', 'large_test_image_nikon.NEF'])
def test_invoke_handler_large_file(
        eventbridge_event,
        lambda_client,
        lambda_function_name,
        image_name
    ):
    '''Test invoking handler and a large file.'''
    resp = lambda_client.invoke(
        FunctionName=lambda_function_name,
        LogType='Tail',
        Payload=json.dumps(eventbridge_event).encode('utf-8')
    )
    resp_body = json.loads(resp.pop('Payload').read().decode())

    assert resp['StatusCode'] == 200
    assert resp_body == {}


@pytest.mark.skip(reason='TODO')
def test_put_event():
    '''Test putting event on EventBridge'''
    pass

@pytest.mark.skip(reason='Not sure how to check failure occurred')
def test_put_event_failed_txn():
    '''Test some failed transactions'''
    pass
