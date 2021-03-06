'''PhotoOpsAI photo data'''

from dataclasses import dataclass
from datetime import datetime
from typing import Union


@dataclass
class PhotoData:
    '''PhotoData data'''

    file_name: str
    file_suffix: Union[str, None]
    size: int

    @dataclass
    class S3Location:
        '''Image S3 location'''
        bucket: str
        key: str

    location: S3Location

    @dataclass
    class JpegLocation:
        '''JPEG cached image'''
        bucket: str
        key: str
        expiration: datetime

    jpeg_location: JpegLocation
