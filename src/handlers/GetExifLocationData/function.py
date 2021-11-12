'''Return normalized location EXIF data'''

from dataclasses import asdict, dataclass
from typing import Any, Dict, cast

from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from common.models import ExifDataItem, Ifd, LocationExifData, LocationExifDataItem, PutDdbItemAction
from common.util.dataclasses import lambda_dataclass_response

LOGGER = Logger(utc=True)


@dataclass
class Response(PutDdbItemAction):
    '''Function response'''
    Item: LocationExifDataItem


def _get_exif_location_data(exif_data: ExifDataItem) -> LocationExifData:
    '''Return normalized location data'''
    ifd0 = cast(Ifd, exif_data.exif.ifd0)
    ifd0.gps_ifd
    location_data = {}
    location_data['gps_version_id'] = ifd0.gps_ifd.gps_version_id
    location_data['gps_latitude_ref'] = ifd0.gps_ifd.gps_latitude_ref
    location_data['gps_latitude'] = ifd0.gps_ifd.gps_latitude
    location_data['gps_longitude_ref'] = ifd0.gps_ifd.gps_longitude_ref
    location_data['gps_longitude'] = ifd0.gps_ifd.gps_longitude
    location_data['gps_altitude_ref'] = ifd0.gps_ifd.gps_altitude_ref
    location_data['gps_altitude'] = ifd0.gps_ifd.gps_altitude
    location_data['gps_time_stamp'] = ifd0.gps_ifd.gps_time_stamp
    location_data['gps_satellites'] = ifd0.gps_ifd.gps_satellites
    location_data['gps_map_datum'] = ifd0.gps_ifd.gps_map_datum
    location_data['gps_date'] = ifd0.gps_ifd.gps_date

    return LocationExifData(**location_data)


@LOGGER.inject_lambda_context
@lambda_dataclass_response
def handler(event: Dict[str, Any], context: LambdaContext) -> Response:
    '''Function entry'''
    LOGGER.info('Event', extra={"message_object": event})

    pk = event.get('pk')
    sk = 'location#v0'
    exif_data = ExifDataItem(**event)
    location_data = _get_exif_location_data(exif_data)
    location_data_item = LocationExifDataItem(
        **{
            'pk': pk,
            'sk': sk,
            **location_data.__dict__
        }
    )

    response = Response(**{'Item': location_data_item})

    LOGGER.info('Response', extra={"message_object": response})

    return response
