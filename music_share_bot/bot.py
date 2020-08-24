import requests
from telebot import types
from .music.api.apple_music.api import AppleMusicApi
import re
import threading
import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import telebot

logger = telebot.logger
spotify = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
apple_music = AppleMusicApi(requests.session())


class MusicShareBot(threading.Thread):
    def __init__(self, telebot_instanse: telebot.TeleBot, error_reload_interval: int = 10,
                    polling_interval: float = 0.2):
        super().__init__()
        self.bot = telebot_instanse
        self.error_reload_interval = error_reload_interval
        self.polling_interval = polling_interval

    def start_polling(self) -> None:
        @self.bot.inline_handler(func=lambda query: re.findall('^[\w\s]+$', query.query))
        def handle_item_link_to_spotify_url_inline(query):
            logger.info(f'Inline query {query.id} with hint {query.query}')
            logger.info(query)

            results = apple_music.make_search_query(term=query.query, limit=5)
            if not results.top_results:
                telebot_query_result = [types.InlineQueryResultArticle(
                    id=1, title='Not found', description='Try to find something another.',
                    input_message_content=types.InputTextMessageContent(
                    message_text='Not found'
                )
                )]
                self.bot.answer_inline_query(query.id, telebot_query_result)
            telebot_query_result = []
            shared_result = []
            for result in results.top_results:
                if result.__class__.__name__ == 'Song':
                    search_query = f'{result.artist_name} - {result.name}'
                    spotify_result = spotify.search(search_query, limit=10, type='track')['tracks']['items']
                    try:
                        spotify_result = spotify_result[0]
                    except:
                        logger.warning(f'Song \"{search_query}\" not found.')
                        continue
                    duration = int(result.duration / 1000)
                    str_genres = ', '.join(result.genre_names)
                    shared_result.append(
                        {
                            'artwork': result.artwork,
                            'name': f'{result.artist_name} - {result.name} ({duration//60}:{duration%60})',
                            'description': f'Track - {str_genres} - {result.release_date}',
                            'links': {
                                'spotify': spotify_result['external_urls']['spotify'],
                                'apple_music': result.url
                            }
                        }
                    )
                if result.__class__.__name__ == 'Artist':
                    search_query = f'{result.name}'
                    spotify_result = spotify.search(search_query, limit=10, type='artist')['artists']['items']
                    try:
                        spotify_result = spotify_result[0]
                    except:
                        logger.warning(f'Artist \"{search_query}\" not found.')
                        continue
                    str_genres = ', '.join(result.genre_names)
                    shared_result.append(
                        {
                            'artwork': result.artwork,
                            'name': f'{result.name}',
                            'description': f'Artist - {str_genres}',
                            'links': {
                                'spotify': spotify_result['external_urls']['spotify'],
                                'apple_music': result.url
                            }
                        }
                    )
                if result.__class__.__name__ == 'Album':
                    search_query = f'{result.artist_name} - {result.name}'
                    spotify_result = spotify.search(search_query, limit=10, type='album')['albums']['items']
                    try:
                        spotify_result = spotify_result[0]
                    except:
                        logger.warning(f'Album \"{search_query}\" not found.')
                        continue
                    str_genres = ', '.join(result.genre_names)
                    shared_result.append(
                        {
                            'artwork': result.artwork,
                            'name': f'{result.artist_name} - {result.name}',
                            'description': f'Album - {result.track_count} tracks - {str_genres} - {result.release_date}',
                            'links': {
                                'spotify': spotify_result['external_urls']['spotify'],
                                'apple_music': result.url
                            }
                        }
                    )

            for instanse_num, instanse in enumerate(shared_result):
                spotify_link = instanse['links']['spotify']
                amusic_link = instanse['links']['apple_music']
                message_content = types.InputTextMessageContent(
                    message_text=f'[Spotify]({spotify_link})\n[Apple Music]({amusic_link})', parse_mode='Markdown'
                )
                telebot_query_result.append(types.InlineQueryResultArticle(
                    id=instanse_num+1, title=instanse['name'], description=instanse['description'],
                    input_message_content=message_content, thumb_url=instanse['artwork'].url, thumb_width=48,
                    thumb_height=48
                ))
            
            logger.info(f'Send inline answer to query {query.id} with hint {query.query}')

            self.bot.answer_inline_query(query.id, telebot_query_result)

        @self.bot.inline_handler(func=lambda query: True)
        def catch_every_inline_message(query):
            logger.info('Bot catched strange inline query.')
            logger.debug(query)

        @self.bot.message_handler(commands=['start'])
        def handle_message(message):
            user_name = (' '.join(
                message.from_user.first_name,
                message.from_user.last_name
                )) if message.from_user.last_name else message.from_user.first_name
            logger.info(f'New message \"{message.text}\" from user {user_name} in chat {message.chat.id}. Send answer.')
            self.bot.reply_to(
                message,
                'Hello!👽\n'
            )

        @self.bot.message_handler(commands=['help'])
        def handle_message(message):
            user_name = (' '.join(
                message.from_user.first_name,
                message.from_user.last_name
                )) if message.from_user.last_name else message.from_user.first_name
            logger.info(f'New message \"{message.text}\" from user {user_name} in chat {message.chat.id}. Send answer.')
            self.bot.reply_to(
                message,
                'Use inline mode!'
            )

        @self.bot.message_handler(func=lambda message: True)
        def handle_strange_message(message):
            user_name = (' '.join(
                message.from_user.first_name,
                message.from_user.last_name
                )) if message.from_user.last_name else message.from_user.first_name
            logger.info(f'New strange message \"{message.text}\" from user {user_name} in chat {message.chat.id}. Send answer.')
            logger.debug(message)

            self.bot.reply_to(message, text='Use inline mode!')
        
        self.bot.polling(none_stop=True, interval=self.polling_interval)

    def run(self) -> None:
        while True:
            try:
                self.start_polling()
            except Exception as err:
                logger.error(err)
                logger.info(f'Reload bot polling in {self.error_reload_interval} seconds')
                time.sleep(self.error_reload_interval)
