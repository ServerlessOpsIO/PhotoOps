'''Return normalized Lens EXIF data'''

from dataclasses import asdict, dataclass
from typing import Any, Dict, Union, cast

from aws_lambda_powertools.logging import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from common.models import ExifDataItem, Ifd, LensExifData, LensExifDataItem, PutDdbItemAction
from common.util.dataclasses import lambda_dataclass_response

LOGGER = Logger(utc=True)


@dataclass
class Response(PutDdbItemAction):
    '''Function response'''
    Item: LensExifDataItem


def _get_lens_focal_attrs(ifd: Ifd) -> Dict[str, Union[int, float, None]]:
    '''Return lens focal attributes'''
    focal_attrs = ifd.maker_note.lens_min_max_focal_max_aperture
    return {
        'min_focal': int(focal_attrs[0]),
        'max_focal': int(focal_attrs[1]),
        'min_aperture': None,
        'max_aperture_high': focal_attrs[2],
        'max_aperture_low': focal_attrs[3],
    }



def _get_exif_lens_data(exif_data: ExifDataItem) -> LensExifData:
    '''Return normalized lens data'''
    ifd = cast(Ifd, exif_data.exif.ifd0)

    lens_data = {
        **_get_lens_focal_attrs(ifd)
    }

    lens_data['lens_maker_type'] = []
    lens_data['camera_maker_type'] = ifd.maker_note.lens_type.split(' ')

    lens_data['auto_focus'] = True if lens_data['camera_maker_type'][0] == 'AF' else False
    lens_data['vibration_reduction'] = True if 'VR' in lens_data['camera_maker_type'] else False

    # These are in LensData which I don't know how to read
    lens_data['make'] = None
    lens_data['model'] = None
    lens_data['serial_number'] = None
    lens_data['macro'] = None
    lens_data['zoom'] = True if lens_data['min_focal'] != lens_data['max_focal'] else False

    return LensExifData(**lens_data)


@LOGGER.inject_lambda_context
@lambda_dataclass_response
def handler(event: Dict[str, Any], context: LambdaContext) -> Response:
    '''Function entry'''
    LOGGER.info('Event', extra={"message_object": event})

    pk = event.get('pk')
    sk = 'lens#v0'
    exif_data = ExifDataItem(**event)
    lens_data = _get_exif_lens_data(exif_data)
    lens_data_item = LensExifDataItem(
        **{
            'pk': pk,
            'sk': sk,
            **lens_data.__dict__
        }
    )

    response = Response(**{'Item': lens_data_item})

    LOGGER.info('Response', extra={"message_object": asdict(response)})

    return response
