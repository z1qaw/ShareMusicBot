import threading

import requests
import telebot
from telebot import types

from ..api.apple_music.api import AppleMusicApi
from .api_services.manager_data import ServiceDataRequestQuery
from .api_services.spotify_service_thread import SpotifyServiceThread
from .api_services.yandex_music_service_thread import YandexMusicServiceThread

logger = telebot.logger


class ApiManagerService(threading.Thread):
    def __init__(self, music_share_bot):
        super().__init__()
        self.session = requests.session()
        self.music_share_bot = music_share_bot
        self.search_results_count = 4
        self.completed_api_requests = []
        self.incompleted_main_results = []
        
        self.api_workers = {
            'spotify': [],
            'yandex_music': []
        }

        self.apple_music_api = AppleMusicApi(self.session)

        for _ in range(self.search_results_count):
            spotify_service = SpotifyServiceThread(manager=self)
            spotify_service.start()
            self.api_workers['spotify'].append(spotify_service)

            yamusic_service = YandexMusicServiceThread(manager=self, session=requests.session())
            yamusic_service.start()
            self.api_workers['yandex_music'].append(yamusic_service)

    def put_task(self, query):
        logger.debug(
            f'Search in Apple Music and get top-{self.search_results_count} results...'
        )
        main_results = self.apple_music_api.make_search_query(
            term=query.query,
            limit=self.search_results_count
        )

        self.incompleted_main_results.append(
            {
                'telebot_query_id': query.id,
                'result': main_results
            }
        )

        if not main_results.top_results:
            telebot_query_result = [types.InlineQueryResultArticle(
                id=1, title='Not found', description='Try to find something another',
                input_message_content=types.InputTextMessageContent(
                message_text='Not found'
            )
            )]
            self.music_share_bot.bot.answer_inline_query(query.id, telebot_query_result)
            return

        for service_name in self.api_workers:
            for worker in self.api_workers[service_name]:
                result_num = self.api_workers[service_name].index(worker)
                result = main_results.top_results[result_num]
                apple_music_object_name = result.__class__.__name__
                query_scheme = {
                    'Song': {
                        'search_query': '{} - {}'.format(
                            result.artist_name,
                            result.name
                        ) if apple_music_object_name == 'Song' else None,
                        'spotify_object_name': 'track',
                        'yandex_music_object_name': 'track'
                    },
                    'Album': {
                        'search_query': '{} - {}'.format(
                            result.artist_name,
                            result.name
                        ) if apple_music_object_name == 'Album' else None,
                        'spotify_object_name': 'album',
                        'yandex_music_object_name': 'album'
                    },
                    'Artist': {
                        'search_query': result.name 
                            if apple_music_object_name == 'Artist' else None,
                        'spotify_object_name': 'artist',
                        'yandex_music_object_name': 'artist'
                    }
                }
                object_scheme = query_scheme[apple_music_object_name]
                search_query = object_scheme['search_query']
                worker.append_search_query_task(ServiceDataRequestQuery(
                    bot_inline_query_id=query.id,
                    main_result_id=result_num,
                    service_name=service_name,
                    query_text=search_query,
                    query_data_type=object_scheme[service_name + '_object_name'],
                    completed=False,
                    bad=False,
                    result=None
                ))

    def append_completed_query_task(self, query_task: ServiceDataRequestQuery):
        self.completed_api_requests.append(query_task)
        found_requests = [
            task for task in self.completed_api_requests
            if task.bot_inline_query_id == query_task.bot_inline_query_id
        ]
        if len(found_requests) == self.search_results_count * len(self.api_workers):
            found_main_query = [
                main_query for main_query in self.incompleted_main_results
                if main_query['telebot_query_id'] == query_task.bot_inline_query_id
            ][0]

            telebot_query_result = []
            for instanse_num, result_instanse in enumerate(found_main_query['result'].top_results):
                additional_results = {
                    'spotify': [
                        result for result in found_requests 
                        if (result.main_result_id == instanse_num and result.service_name == 'spotify')
                    ][0],
                    'yandex_music': [
                        result for result in found_requests 
                        if (result.main_result_id == instanse_num and result.service_name == 'yandex_music')
                    ][0]
                }
                spotify_link = additional_results['spotify'].result['external_urls']['spotify'] \
                    if not additional_results['spotify'].bad else ''
                amusic_link = result_instanse.url
                ym_link = additional_results['yandex_music'].result.url \
                    if not additional_results['yandex_music'].bad else ''
                thumb_url = result_instanse.artwork.url

                apple_music_object_name = result_instanse.__class__.__name__
                telebot_query_name = ''
                telebot_query_description = ''
                filtered_genres = list(filter(
                    lambda genre_name: genre_name not in ['Музыка'],
                    result_instanse.genre_names
                ))
                str_genres = ', '.join(filtered_genres)

                if apple_music_object_name == 'Song':
                    duration = int(result_instanse.duration / 1000)
                    telebot_query_name = f'{result_instanse.artist_name} - {result_instanse.name} ({duration//60}:{duration%60})'
                    telebot_query_description = f'Track - {str_genres} - {result_instanse.release_date}'
                if apple_music_object_name == 'Artist':
                    telebot_query_name = f'{result_instanse.name}'
                    telebot_query_description = f'Artist - {str_genres}'
                if apple_music_object_name == 'Album':
                    telebot_query_name = f'{result_instanse.artist_name} - {result_instanse.name}'
                    telebot_query_description = f'Album - {result_instanse.track_count} tracks - {str_genres} - {result_instanse.release_date}'

                message_content = types.InputTextMessageContent(
                    message_text=f'[Spotify]({spotify_link})\n[Apple Music]({amusic_link})\n[Yandex Music]({ym_link})', parse_mode='Markdown'
                )
                telebot_query_result.append(types.InlineQueryResultArticle(
                    id=instanse_num+1, title=telebot_query_name, description=telebot_query_description,
                    input_message_content=message_content, thumb_url=thumb_url, thumb_width=48,
                    thumb_height=48
                ))

            self.music_share_bot.bot.answer_inline_query(
                found_main_query['telebot_query_id'],
                telebot_query_result
            )


    def run(self):
        pass
