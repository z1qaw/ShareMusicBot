from typing import Literal, Set

import requests

from .api_data_utils import search_query_answer_json_dict_to_class


class AppleMusicApi:
    def __init__(self, session: requests.Session):
        self.session = session
        self.api_host = 'https://amp-api.music.apple.com'
        self.auth_key = 'Bearer eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IldlYlBsYXlLaWQifQ.eyJpc3MiOiJBTVBXZWJQbGF5IiwiaWF0IjoxNTk4NDE4MjQwLCJleHAiOjE2MTM5NzAyNDB9.FemTn31_pZp3RY88DLQWKtn13gyj3uNcqBYwUi7zbNPN8mKgexKu36sOoDI7F4dBqOSmKZaBeiafXINRgPPgSw'

    def make_api_request(self, api_method_path, params):
        api_method_url = self.api_host + api_method_path
        headers = {
            'authorization': self.auth_key
        }
        data = self.session.get(api_method_url, params=params, headers=headers).json()
        return data

    def make_search_query(self, term: str, limit: int = 25,
            types: Set[Literal['artists', 'albums', 'songs']] = {'artists', 'albums', 'songs'}):
        api_method_path = '/v1/catalog/ru/search'
        params = {
            'term': term,
            'types': ','.join(list(types)),
            'limit': limit,
            'with': 'serverBubbles'
        }
        api_response_data = self.make_api_request(api_method_path=api_method_path, params=params)
        return search_query_answer_json_dict_to_class(api_response_data)
