from dataclasses import asdict
from typing import Any, Callable, Dict

from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from aws_lambda_powertools.utilities.typing import LambdaContext
from boto3.dynamodb.types import TypeSerializer


import boto3

@lambda_handler_decorator
def serialize_ddb_item(handler: Callable[..., Any], event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    '''
    Serialize the Item data into a format suitable for the DDB API.
    '''
    response = handler(event, context)

    ddb_items = response.get('Item')
    response['Item'] = { k: TypeSerializer().serialize(v) for k, v in ddb_items.items() }

    return response
