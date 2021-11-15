'''Ingest S3 event and publish event data.'''

import json

from typing import Any, Dict

from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.tracing import Tracer
from aws_lambda_powertools.utilities.data_classes import SNSEvent, S3Event
from aws_lambda_powertools.utilities.typing import LambdaContext

TRACER = Tracer()
LOGGER = Logger(utc=True)

@TRACER.capture_lambda_handler
@LOGGER.inject_lambda_context
def handler(event: Dict[str, Any], context: LambdaContext) -> dict:
    '''Function entry'''

    LOGGER.info('Event', extra={"message_object": event})
    sns_event = SNSEvent(event)
    sns_message_str = json.loads(sns_event.sns_message)
    s3_event = S3Event(sns_message_str)
    s3_event_data = s3_event._data

    LOGGER.info('Response', extra={"message_object": s3_event_data})
    return s3_event_data
