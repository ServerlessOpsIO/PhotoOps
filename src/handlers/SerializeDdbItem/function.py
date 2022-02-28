'''
Take in DDB Document Item data and serialize into DDB API Item data.
'''
import json
from decimal import Decimal
from typing import Any, Dict

from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from boto3.dynamodb.types import TypeSerializer

LOGGER = Logger(utc=True)


@LOGGER.inject_lambda_context
def handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    '''
    Serialize the Item data into a format suitable for the DDB API.
    '''

    # Floats are not supported by DDB.
    event = json.loads(json.dumps(event), parse_float=Decimal)
    if event.get('Item') is not None:
        ddb_items = event.get('Item')
        event['Item'] = { k: TypeSerializer().serialize(v) for k, v in ddb_items.items() }
    if event.get('Key') is not None:
        ddb_key = event.get('Key')
        event['Key'] = { k: TypeSerializer().serialize(v) for k, v in ddb_key.items() }


    return event
