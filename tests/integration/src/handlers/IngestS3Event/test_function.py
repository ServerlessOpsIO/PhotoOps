'''Test IngestS3Event'''

import json
import os

import boto3

import pytest
from aws_lambda_powertools.utilities.data_classes import S3Event
from mypy_boto3_cloudformation import CloudFormationClient
from mypy_boto3_lambda import LambdaClient

STACK_NAME = os.environ.get('STACK_NAME')
FUNCTION_LOGICAL_ID = 'IngestS3Event'
SNS_TOPIC_LOGICAL_ID = 'PhotoOpsIngestTopic'

DATA_DIR = './data'
EVENT_DIR = os.path.join(DATA_DIR, 'events')
IMAGE_DIR = os.path.join(DATA_DIR, 'images')
MODEL_DIR = os.path.join(DATA_DIR, 'models')

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


### Events
@pytest.fixture()
def base_sns_event():
    '''Return a test event'''
    with open(os.path.join(EVENT_DIR, 'IngestS3Event-event-sns.json')) as f:
        return json.load(f)

@pytest.fixture(params=['IngestS3Event-data-put.json'])
def generic_s3_put_notification(request):
    '''Return an S3 PUT notification'''
    with open(os.path.join(EVENT_DIR, request.param)) as f:
        return json.load(f)


@pytest.fixture(params=['IngestS3Event-data-delete.json'])
def generic_s3_delete_notification(request):
    '''Return an S3 DELETE notification'''
    with open(os.path.join(EVENT_DIR, request.param)) as f:
        return json.load(f)

@pytest.fixture
def generic_sns_s3_put_event(base_sns_event, generic_s3_put_notification):
    '''Return an s3 put event'''
    s3_notification_event = S3Event(generic_s3_put_notification)
    base_sns_event['Records'][0]['Sns']['Message'] = json.dumps(s3_notification_event._data)
    return base_sns_event

@pytest.fixture
def generic_sns_s3_delete_event(base_sns_event, generic_s3_delete_notification):
    '''Return an s3 put event'''
    s3_notification_event = S3Event(generic_s3_delete_notification)
    base_sns_event['Records'][0]['Sns']['Message'] = json.dumps(s3_notification_event._data)
    return base_sns_event


def test_invoke_handler_s3_put(generic_sns_s3_put_event, generic_s3_put_notification, lambda_client, lambda_function_name):
    '''Test invoking handler with a PUT event'''
    resp = lambda_client.invoke(
        FunctionName=lambda_function_name,
        LogType='Tail',
        Payload=json.dumps(generic_sns_s3_put_event).encode('utf-8')
    )
    resp_body = resp.pop('Payload').read().decode()

    assert resp['StatusCode'] == 200
    assert json.loads(resp_body) == generic_s3_put_notification

def test_invoke_handler_s3_delete(generic_sns_s3_delete_event, generic_s3_delete_notification, lambda_client, lambda_function_name):
    '''
    Test invoking with a DELETE event

    We may want to process DELETEs in a way at a later date so the function
    blindly unwraps and publishes. We rely on EventBridge to then filter
    messages correctly.
    '''
    resp = lambda_client.invoke(
        FunctionName=lambda_function_name,
        LogType='Tail',
        Payload=json.dumps(generic_sns_s3_delete_event).encode('utf-8')
    )
    resp_body = resp.pop('Payload').read().decode()

    assert resp['StatusCode'] == 200
    assert json.loads(resp_body) == generic_s3_delete_notification
