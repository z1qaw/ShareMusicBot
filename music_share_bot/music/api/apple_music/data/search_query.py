import dataclasses
from typing import Set, Tuple, Union

from .album import Album
from .artist import Artist
from .song import Song


@dataclasses.dataclass
class SearchAnswer:
    top_results: Tuple[Union[Song, Album, Artist]]
    songs: Tuple[Song]
    albums: Tuple[Album]
    artists: Tuple[Artist]
    order: Set[str]
