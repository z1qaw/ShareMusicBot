import dataclasses
import datetime
from music_share_bot.music.api.apple_music.data.artwork import Artwork
from typing import Set


@dataclasses.dataclass
class Song:
    id: int
    href: str
    artist_name: str
    url: str
    duration: int
    release_date: datetime.date
    name: str
    album_name: str
    genre_names: Set[str]
    artwork: Artwork
