# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
'''Test IngestS3Event'''

import json
import os

import pytest

from collections import namedtuple

from aws_lambda_powertools.utilities.data_classes import S3Event

import src.handlers.IngestS3Event.function as func

DATA_DIR = './data'
EVENT_DIR = os.path.join(DATA_DIR, 'events')
IMAGE_DIR = os.path.join(DATA_DIR, 'images')
MODEL_DIR = os.path.join(DATA_DIR, 'models')

### Events
@pytest.fixture()
def context():
    '''context object'''
    function_name = 'IngestS3Event'
    context_info = {
        'aws_request_id': '00000000-0000-0000-0000-000000000000',
        'function_name': function_name,
        'invoked_function_arn': 'arn:aws:lambda:us-east-1:012345678910:function:{}'.format(function_name),
        'memory_limit_in_mb': 128
    }

    context = namedtuple("LambdaContext", context_info.keys())
    return context._make(context_info.values())

@pytest.fixture()
def event():
    '''Return a test event'''
    with open(os.path.join(EVENT_DIR, 'IngestS3Event-event-sns.json')) as f:
        return json.load(f)

@pytest.fixture()
def event_schema():
    '''Return an event schema'''
    with open(os.path.join(EVENT_DIR, 'lambda-sns-event.schema.json')) as f:
        return json.load(f)


@pytest.fixture(params=['IngestS3Event-data-put.json', 'IngestS3Event-data-delete.json'])
def s3_notification(request):
    '''Return an S3 notification'''
    with open(os.path.join(EVENT_DIR, request.param)) as f:
        return json.load(f)


@pytest.fixture()
def s3_notification_schema():
    '''Return an S3 notification schema'''
    with open(os.path.join(EVENT_DIR, 's3-notification.schema.json')) as f:
        return json.load(f)



### Tests
def test_handler(event, s3_notification, context, mocker):
    '''Call handler'''

    s3_notification_event = S3Event(s3_notification)
    event['Records'][0]['Sns']['Message'] = json.dumps(s3_notification_event._data)

    resp = func.handler(event, context)

    assert resp == s3_notification

