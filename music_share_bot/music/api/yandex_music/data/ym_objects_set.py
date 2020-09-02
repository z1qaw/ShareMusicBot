import dataclasses
from typing import Tuple, Union

from .album import Album
from .artist import Artist
from .track import Track


@dataclasses.dataclass
class ObjectsSet:
    object_type: str
    items: Tuple[Union[Track, Album, Artist]]
    total: int
    per_page: int
    order: int
