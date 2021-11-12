'''Ingest S3 event and publish event data.'''

import json
import logging
import os

from typing import Any, Dict

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.data_classes import SNSEvent, S3Event
from aws_lambda_powertools.utilities.typing import LambdaContext

LOGGER = Logger(utc=True)

@LOGGER.inject_lambda_context(log_event=True)
def handler(event: Dict[str, Any], context: LambdaContext) -> dict:
    '''Function entry'''

    sns_event = SNSEvent(event)
    sns_message_str = json.loads(sns_event.sns_message)
    s3_event = S3Event(sns_message_str)
    s3_event_data = s3_event._data

    LOGGER.info('Response', extra={"message_object": s3_event_data})
    resp = s3_event_data
    return resp
