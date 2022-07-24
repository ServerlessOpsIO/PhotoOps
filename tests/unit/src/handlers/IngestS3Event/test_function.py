# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
'''Test IngestS3Event'''

import json
import os
import pytest

from aws_lambda_powertools.utilities.data_classes import S3Event
from common.test.aws import create_lambda_function_context

import src.handlers.IngestS3Event.function as func

FUNCTION_NAME = 'IngestS3event'

DATA_DIR = './data'
COMMON_DATA_DIR = os.path.join(DATA_DIR, 'common')
FUNC_DATA_DIR = os.path.join(DATA_DIR, 'handlers', FUNCTION_NAME)

EVENT = os.path.join(FUNC_DATA_DIR, 'event.json')
EVENT_SCHEMA = os.path.join(FUNC_DATA_DIR, 'event.schema.json')
DATA = [os.path.join(FUNC_DATA_DIR, f) for f in ['data-S3Put.json', 'data-S3Delete.json']]
DATA_SCHEMA = os.path.join(FUNC_DATA_DIR, 'data.schema.json')
OUTPUT_SCHEMA = DATA_SCHEMA

@pytest.fixture()
def context():
    '''context object'''
    return create_lambda_function_context(FUNCTION_NAME)

@pytest.fixture()
def event():
    '''Return a test event'''
    with open(EVENT) as f:
        return json.load(f)

@pytest.fixture()
def event_schema():
    '''Return an event schema'''
    with open(EVENT_SCHEMA) as f:
        return json.load(f)


@pytest.fixture(params=DATA)
def data(request):
    '''Return an S3 notification'''
    with open(request.param) as f:
        return json.load(f)


@pytest.fixture()
def data_schema():
    '''Return an S3 notification schema'''
    with open(DATA_SCHEMA) as f:
        return json.load(f)


@pytest.fixture()
def expected_output(data):
    '''Return an S3 notification'''
    return data


@pytest.fixture()
def expected_output_schema():
    '''Return an S3 notification schema'''
    with open(OUTPUT_SCHEMA) as f:
        return json.load(f)



### Tests
def test_handler(event, data, expected_output, context, mocker):
    '''Call handler'''

    s3_notification = S3Event(data)
    event['Records'][0]['Sns']['Message'] = json.dumps(s3_notification._data)

    resp = func.handler(event, context)

    assert resp == expected_output

