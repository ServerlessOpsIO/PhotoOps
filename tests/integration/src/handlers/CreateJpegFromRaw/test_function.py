'''Test CreateJpgFromRaw'''

import json
import os

import boto3

import pytest
from aws_lambda_powertools.utilities.data_classes import S3Event
from mypy_boto3_cloudformation import CloudFormationClient
from mypy_boto3_lambda import LambdaClient
from mypy_boto3_events import EventsClient

STACK_NAME = os.environ.get('STACK_NAME')
FUNCTION_LOGICAL_ID = 'CreateJpegFromRaw'
EVENT_BUS_LOGICAL_ID = 'EventBus'
IMAGE_BUCKET_PATH = os.environ.get('TEST_PHOTO_IMAGE_BUCKET_PATH', 'DUMMY_BUCKET').strip('/').split('/', 1)
BUCKET_NAME = IMAGE_BUCKET_PATH[0]
BUCKET_PATH = IMAGE_BUCKET_PATH[1].strip('/') if len(IMAGE_BUCKET_PATH) > 1 else ''

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
def events_client(session) -> EventsClient:
    '''Return an SNS client'''
    return session.client('sns')

@pytest.fixture()
def eventbus_name(cfn_client) -> str:
    '''Return the EventBus name'''
    eventbus_name = cfn_client.describe_stack_resource(
        StackName=STACK_NAME,
        LogicalResourceId=EVENT_BUS_LOGICAL_ID
    )
    return eventbus_name['StackResourceDetail']['PhysicalResourceId']


### Events