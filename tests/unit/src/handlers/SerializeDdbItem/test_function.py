# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
'''Test IngestS3Event'''

import json
import os

import pytest

from common.test.aws import create_lambda_function_context

try:
    import src.handlers.SerializeDdbItem.function as func
except:
    pytestmark = pytest.mark.skip


DATA_DIR = './data'
EVENT_DIR = os.path.join(DATA_DIR, 'events')

#EVENT = os.path.join(EVENT_DIR, 'GetExifData-output-test_image_nikon.NEF.json')
#EVENT = os.path.join(EVENT_DIR, 'GetFileData-output.json')
#RESPONSE = os.path.join(EVENT_DIR, 'SerializeDdbItem-output-GetFileData.json')
EVENT = os.path.join(EVENT_DIR, 'GetExifImageData-output.json')
RESPONSE = os.path.join(EVENT_DIR, 'SerializeDdbItem-output-GetExifImageData.json')


### Fixtures
@pytest.fixture()
def context():
    '''context object'''
    return create_lambda_function_context('SerializeDdbItem')

@pytest.fixture()
def event() -> dict:
    '''Return a test event'''
    with open(EVENT) as f:
        return json.load(f)

@pytest.fixture()
def expected_response() -> dict:
    '''Return DDB item'''
    with open(RESPONSE) as f:
        return json.load(f)



### Tests
def test_handler(event: dict, expected_response: dict, context):
    '''Call handler'''

    response = func.handler(event, context)
    print(json.dumps(response, indent=2))

    assert response == expected_response
