from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from aws_lambda_powertools.utilities.typing import LambdaContext
from dataclasses import asdict
from typing import Any, Callable, Dict

from aws_lambda_powertools import Logger
LOGGER = Logger(utc=True, child=True)

@lambda_handler_decorator
def lambda_dataclass_response(handler: Callable[..., Any], event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    LOGGER.info('Event', extra={'message_body': event})
    response = handler(event, context)
    LOGGER.info('Response', extra={'message_body': response})
    return asdict(response)