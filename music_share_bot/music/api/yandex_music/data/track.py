import dataclasses


@dataclasses.dataclass
class Track:
    id: int
    release_year: str
    album_id: int
    cover_uri: str
    duration: int
    explicit: bool
    artist_id: int
    artist_name: str
    name: str

    def __post_init__(self):
        self.url = f'https://music.yandex.ru/album/{self.album_id}/track/{self.id}'