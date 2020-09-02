import dataclasses


@dataclasses.dataclass
class Album:
    id: int
    release_year: int
    cover_uri: str
    artist_name: str
    artist_id: int
    name: str
    genre: str

    def __post_init__(self):
        self.url = f'https://music.yandex.ru/album/{self.id}'