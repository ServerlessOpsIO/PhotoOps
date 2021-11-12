'''Return normalized location EXIF data'''

from dataclasses import asdict, dataclass
from typing import Any, Dict, cast

from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from common.models import ExifDataItem, FileDataItem, PutDdbItemAction
from common.util.dataclasses import lambda_dataclass_response

LOGGER = Logger(utc=True)


@dataclass
class Response(PutDdbItemAction):
    '''Function response'''
    Item: FileDataItem


@LOGGER.inject_lambda_context
@lambda_dataclass_response
def handler(event: Dict[str, Any], context: LambdaContext) -> Response:
    '''Function entry'''
    LOGGER.info('Event', extra={"message_object": event})

    pk = event.get('pk')
    sk = 'file#v0'
    exif_data = ExifDataItem(**event)

    response = Response(
        **{
            'Item': {
                'pk': pk,
                'sk': sk,
                **asdict(exif_data.file)
            }
        }
    )
    LOGGER.info('Response', extra={"message_object": response})

    return response
