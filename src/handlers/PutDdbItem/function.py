'''Ingest a new photo into PhotoOps'''

import json
import os

from decimal import Decimal
from typing import Any, Dict

import boto3
from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.tracing import Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

from mypy_boto3_dynamodb import DynamoDBServiceResource
from mypy_boto3_dynamodb.service_resource import Table
from mypy_boto3_dynamodb.type_defs import PutItemOutputTypeDef

TRACER = Tracer()
LOGGER = Logger(utc=True)

DDB: DynamoDBServiceResource = boto3.resource('dynamodb')
DDB_TABLE: Table = DDB.Table(os.environ.get('DDB_TABLE_NAME', ''))


def _put_ddb_item(item: Dict[str, Any]) -> PutItemOutputTypeDef:
    '''Write item to DDB'''
    item['ReturnConsumedCapacity'] = 'NONE'
    response = DDB_TABLE.put_item(**item)
    LOGGER.debug("DDB put_item() response", extra={"message_object": response})
    return response


@TRACER.capture_lambda_handler
@LOGGER.inject_lambda_context
def handler(event: Dict[str, Any], context: LambdaContext) -> PutItemOutputTypeDef:
    '''Function entry'''
    LOGGER.info('Event', extra={"message_object": event})

    # Floats are not supported by DDB.
    event = json.loads(json.dumps(event), parse_float=Decimal)

    resp = _put_ddb_item(event)

    LOGGER.info('Response', extra={"message_object": resp})

    return resp
