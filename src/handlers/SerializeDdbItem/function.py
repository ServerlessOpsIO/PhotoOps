'''
Take in DDB Document Item data and serialize into DDB API Item data.
'''
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

    ddb_items = event.get('Item')
    event['Item'] = { k: TypeSerializer().serialize(v) for k, v in ddb_items.items() }

    return event
