r"""
Camera data

generated by json2python-models v0.2.1 at Wed Sep 29 13:26:12 2021
command: /Users/tom/.local/share/virtualenvs/PhotoOps-5MqeThcN/bin/json2models -s nested --datetime --max-strings-literals 0 -f dataclasses -m CameraExifData data/events/GetExifCameraData-output.json
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class FileData:
    '''file data'''
    file_type: Optional[str]
    extension: Optional[str]
    object_size: Optional[str]
    is_jpeg: Optional[bool]
    is_raw: Optional[bool]


@dataclass
class FileDataItem(FileData):
    '''File data DDB item'''
    pk: str = ''
    sk: str = ''
