import dataclasses
from typing import Set

from .artwork import Artwork


@dataclasses.dataclass
class Artist:
    id: int
    href: str
    name: str
    artwork: Artwork
    url: str
    genre_names: Set[str]
