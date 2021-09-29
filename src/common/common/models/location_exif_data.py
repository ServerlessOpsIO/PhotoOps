r"""
Location data

generated by json2python-models v0.2.1 at Wed Sep 29 13:27:30 2021
command: /Users/tom/.local/share/virtualenvs/PhotoOps-5MqeThcN/bin/json2models -s nested --datetime --max-strings-literals 0 -f dataclasses -m LocationExifData data/events/GetExifLocationData-output.json
"""
from dataclasses import dataclass, field
from json_to_models.dynamic_typing import IntString
from typing import List, Optional, Union

from .put_ddb_item import PutDdbItemAction

@dataclass
class LocationExifData:
    '''Location EXIF data'''
    gps_version_id: Optional[List[int]]
    gps_latitude_ref: Optional[str]
    gps_latitude: Optional[List[float]]
    gps_longitude_ref: Optional[str]
    gps_longitude: Optional[List[float]]
    gps_altitude_ref: Optional[int]
    gps_altitude: Optional[float]
    gps_timestamp: Optional[List[float]]
    gps_satellites: Optional[IntString]
    gps_map_datum: Optional[str]
    gps_date: Optional[str]


@dataclass
class LocationExifDataItem(LocationExifData):
    '''Location EXIF data DDB item'''
    pk: str = ''
    sk: str = ''

@dataclass
class LocationExifDataResponse(PutDdbItemAction):
    '''Function response'''
    Item: LocationExifDataItem
