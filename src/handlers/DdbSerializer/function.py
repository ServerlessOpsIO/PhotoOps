'''
Take in DDB Document Item data and serialize into DDB API Item data.
'''
import json
from decimal import Decimal
from typing import Any, Dict

from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

LOGGER = Logger(utc=True)

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            if len(o.as_tuple()[1]) == 1:
                return int(o)
            else:
                return float(o)
        return super(DecimalEncoder, self).default(o)


def _api_to_doc(event):
    '''Serialize a DDB Document to a DDB API Item'''
    if event.get('Item') is not None:
        ddb_items = event.get('Item')
        event['Item'] = { k: TypeSerializer().serialize(v) for k, v in ddb_items.items() }
    if event.get('Key') is not None:
        ddb_key = event.get('Key')
        event['Key'] = { k: TypeSerializer().serialize(v) for k, v in ddb_key.items() }

    return event


def _doc_to_api(event):
    '''Serialize a DDB API Item to a DDB Document'''
    if event.get('Item') is not None:
        ddb_items = event.get('Item')
        event['Item'] = { k: TypeDeserializer().deserialize(v) for k, v in ddb_items.items() }
    if event.get('Key') is not None:
        ddb_key = event.get('Key')
        event['Key'] = { k: TypeDeserializer().deserialize(v) for k, v in ddb_key.items() }

    return event


def _decimal_to_float(event):
    '''
    Converts decimals to floats.
    '''
    return json.loads(json.dumps(event, cls=DecimalEncoder))

def _float_to_decimal(event):
    '''
    Converts floats to decimals.
    '''
    return json.loads(json.dumps(event), parse_float=Decimal)


@LOGGER.inject_lambda_context
def handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    '''
    Serialize the Item data into a format suitable for the DDB API.
    '''
    LOGGER.info('Event', extra={"message_object": event})
    transformed_event = event.copy()

    if transformed_event.get('Item') is not None:
        if type(transformed_event['Item'].get('pk')) is dict:
            transformed_event = _doc_to_api(transformed_event)
            transformed_event = _decimal_to_float(transformed_event)
        else:
            transformed_event = _float_to_decimal(transformed_event)
            transformed_event = _api_to_doc(transformed_event)

    if transformed_event.get('Key') is not None:
        if type(transformed_event['Key'].get('pk')) is dict:
            transformed_event = _doc_to_api(transformed_event)
            transformed_event = _decimal_to_float(transformed_event)
        else:
            transformed_event = _float_to_decimal(transformed_event)
            transformed_event = _api_to_doc(transformed_event)

    LOGGER.info('Transformed Event', extra={"message_object": transformed_event})
    return transformed_event
