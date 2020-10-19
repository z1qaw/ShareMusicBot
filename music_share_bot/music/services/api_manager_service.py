import threading
import time

import requests
import telebot
from telebot import types

from ..api.apple_music.api import AppleMusicApi
from .api_services.manager_data import ServiceDataRequestQuery
from .api_services.spotify_service_thread import SpotifyServiceThread
from .api_services.yandex_music_service_thread import YandexMusicServiceThread
from .utils import duration_in_ms_to_str, apple_music_artist_name_filter, apple_music_track_name_filter

logger = telebot.logger


class ApiManagerService(threading.Thread):
    def __init__(self, music_share_bot):
        """ Описание работы сервиса:
                Инициализация:
                    self.search_results_count - глубина поиска (первые n запросов)
                    На каждый сервис API (Yandex, Spotify) создаётся n Python-потоков.
                    
                Фоновая работа:
                    От Telegram-бота в метод put_task приходит inline-запрос, этот метод
                    сначала отсылает запрос к API Apple Music на поиск, получает ответ.
                    Если ответ пустой (ничего не найдено), то отправляет юзеру inline-ответ
                    о том, что ничего не найдено, и завершает работу метода.
                    Если ответ от Apple Music содержит результат, то метод put_task заносит в
                    self.incompleted_main_results пакет с результатом от Apple Music и ID
                    Telegram inline-запроса от юзера. Далее метод отправляет каждый результат в API-поток каждого сервиса
        """

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

        if not main_results.top_results:
            logger.info(f'No results for query {query.query}')
            telebot_query_result = [types.InlineQueryResultArticle(
                id=1, title='Not found', description='Try to find something another',
                input_message_content=types.InputTextMessageContent(
                message_text='Not found'
            )
            )]
            self.music_share_bot.bot.answer_inline_query(query.id, telebot_query_result)
            return

        self.incompleted_main_results.append(
            {
                'telebot_query_id': query.id,
                'result': main_results
            }
        )

        for service_name in self.api_workers:
            for worker in self.api_workers[service_name]:
                result_num = self.api_workers[service_name].index(worker)
                result = None
                try:
                    result = main_results.top_results[result_num]
                except IndexError:
                    continue
                apple_music_object_name = result.__class__.__name__
                query_scheme = {
                    'Song': {
                        'search_query': '{} - {}'.format(
                            apple_music_artist_name_filter(result.artist_name),
                            apple_music_track_name_filter(result.name)
                        ) if apple_music_object_name == 'Song' else None,
                        'spotify_object_name': 'track',
                        'yandex_music_object_name': 'track'
                    },
                    'Album': {
                        'search_query': '{} - {}'.format(
                            apple_music_artist_name_filter(result.artist_name),
                            apple_music_track_name_filter(result.name)
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

        this_task_main_result = [result for result in self.incompleted_main_results
                                    if result['telebot_query_id'] == query_task.bot_inline_query_id][0]
        is_last_result = len(found_requests) == len(this_task_main_result['result'].top_results) * len(self.api_workers)

        if is_last_result:
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
                    duration = duration_in_ms_to_str(result_instanse.duration)
                    telebot_query_name = f'{result_instanse.artist_name} · {result_instanse.name} ({duration})'
                    telebot_query_description = f'Track · {str_genres} · {result_instanse.release_date}'
                if apple_music_object_name == 'Artist':
                    telebot_query_name = f'{result_instanse.name}'
                    telebot_query_description = f'Artist · {str_genres}'
                if apple_music_object_name == 'Album':
                    telebot_query_name = f'{result_instanse.artist_name} - {result_instanse.name}'
                    telebot_query_description = f'Album · {result_instanse.track_count} tracks · {str_genres} · {result_instanse.release_date}'

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

            self.incompleted_main_results.remove(found_main_query)
            for completed_task in found_requests:
                self.completed_api_requests.remove(completed_task)

    def run(self):
        while True:
            time.sleep(0.5)
            print('incompleted', [r['telebot_query_id'] for r in self.incompleted_main_results])
            print('completed_api', [c.bot_inline_query_id for c in self.completed_api_requests])
