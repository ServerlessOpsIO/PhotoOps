r"""
Camera data

generated by json2python-models v0.2.1 at Wed Sep 29 13:26:12 2021
command: /Users/tom/.local/share/virtualenvs/PhotoOps-5MqeThcN/bin/json2models -s nested --datetime --max-strings-literals 0 -f dataclasses -m CameraExifData data/events/GetExifCameraData-output.json
"""
from dataclasses import dataclass
from json_to_models.dynamic_typing import IntString
from typing import Optional


@dataclass
class CameraExifData:
    '''Camera EXIF data'''
    make: Optional[str]
    model: Optional[str]
    software: Optional[str]
    serial_number: Optional[IntString]


@dataclass
class CameraExifDataItem(CameraExifData):
    '''Camera EXIF data DDB item'''
    pk: str = ''
    sk: str = ''
