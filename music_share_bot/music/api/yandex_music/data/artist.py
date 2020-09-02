import dataclasses
from typing import Set


@dataclasses.dataclass
class Artist:
    id: int
    name: str
    cover_uri: str
    genres: Set[str]

    def __post_init__(self):
        self.url = f'https://music.yandex.ru/artist/{self.id}'
