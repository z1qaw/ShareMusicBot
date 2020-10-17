import re
import threading
import time

import telebot

from .music.services.api_manager_service import ApiManagerService

logger = telebot.logger

class MusicShareBotPolling(threading.Thread):
    def __init__(self, telebot_instanse: telebot.TeleBot, error_reload_interval: int = 10,
                    polling_interval: float = 0.1):
        super().__init__()
        self.bot = telebot_instanse
        self.error_reload_interval = error_reload_interval
        self.polling_interval = polling_interval
        self.search_query_max_results = 6
        self.manager = ApiManagerService(self)


    def start_polling(self) -> None:
        @self.bot.inline_handler(func=lambda query: re.findall('^[\w\s]+$', query.query))
        def handle_item_link_to_spotify_url_inline1(query):
            logger.info(f'Inline query {query.id} with hint {query.query}')
            self.manager.put_task(query)

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
