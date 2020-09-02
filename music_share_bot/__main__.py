import logging
import os
from telebot import TeleBot
import telebot
from .bot import MusicShareBotPolling

logger = telebot.logger
logger.setLevel(logging.INFO)
bot_instanse = TeleBot(os.environ['SHARE_MUSIC_BOT_TOKEN'])
share_music_bot = MusicShareBotPolling(telebot_instanse=bot_instanse)
share_music_bot.start()