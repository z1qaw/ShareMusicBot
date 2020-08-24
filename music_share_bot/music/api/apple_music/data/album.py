import dataclasses
import datetime
from typing import Set

from .artwork import Artwork


@dataclasses.dataclass
class Album:
    id: int
    artwork: Artwork
    artist_name: str
    is_single: bool
    url: str
    is_complete: bool
    genre_names: Set[str]
    track_count: int
    release_date: datetime.date
    name: str
