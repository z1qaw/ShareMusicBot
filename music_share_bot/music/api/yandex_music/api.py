from typing import Literal
import requests
from . import api_data_utils


class YandexMusicApi:
    def __init__(self, session: requests.Session) -> None:
        self.session = session
        self.api_host = 'https://music.yandex.ru'

    def search(self, text: str, object_type: Literal['all', 'albums', 'artists', 'tracks'],
                lang: Literal['ru', 'en']):
        api_method_path = '/handlers/music-search.jsx'
        api_params = {
            'text': text,
            'type': object_type,
            'lang': lang,   
        }
        api_answer = self.session.get(url=self.api_host + api_method_path, params=api_params).json()
        return api_data_utils.compare_ym_search_query_dict(api_answer)
