# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
'''Test IngestS3Event'''

import json
import os

import pytest

from common.test.aws import create_lambda_function_context

try:
    import src.handlers.DdbSerializer.function as func
except:
    pytestmark = pytest.mark.skip


DATA_DIR = './data'
EVENT_DIR = os.path.join(DATA_DIR, 'events')

DOC_ITEM = os.path.join(EVENT_DIR, 'DdbSerializer-doc-item.json')
API_ITEM = os.path.join(EVENT_DIR, 'DdbSerializer-api-item.json')


### Fixtures
@pytest.fixture()
def context():
    '''context object'''
    return create_lambda_function_context('DdbSerializer')

@pytest.fixture()
def doc_item(d=DOC_ITEM) -> dict:
    '''Return a DDB doc item'''
    with open(d) as f:
        return json.load(f)

@pytest.fixture()
def api_item(i=API_ITEM) -> dict:
    '''Return DDB API item'''
    with open(i) as f:
        return json.load(f)

@pytest.fixture()
def doc_key(doc_item) -> dict:
    '''Return a DDB doc key'''
    item = doc_item.pop('Item')
    doc_item['Key'] = item
    return doc_item

@pytest.fixture()
def api_key(api_item) -> dict:
    '''Return DDB API key'''
    item = api_item.pop('Item')
    api_item['Key'] = item
    return api_item


### Tests
def test_handler_with_api_item(api_item: dict, doc_item: dict, context):
    '''Call handler'''
    response = func.handler(api_item, context)

    assert response == doc_item


def test_handler_with_doc_item(doc_item: dict, api_item: dict, context):
    '''Call handler'''
    response = func.handler(doc_item, context)

    assert response == api_item


def test_handler_with_api_key(api_key: dict, doc_key: dict, context):
    '''Call handler'''
    response = func.handler(api_key, context)

    assert response == doc_key


def test_handler_with_doc_key(doc_key: dict, api_key: dict, context):
    '''Call handler'''
    response = func.handler(doc_key, context)

    assert response == api_key
