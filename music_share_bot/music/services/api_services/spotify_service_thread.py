import threading
from queue import LifoQueue

import spotipy
import telebot
from spotipy.oauth2 import SpotifyClientCredentials

from .manager_data import ServiceDataRequestQuery

logger = telebot.logger


class SpotifyServiceThread(threading.Thread):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.api = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
        self.requests_queue = LifoQueue()

    def append_search_query_task(self, query_task: ServiceDataRequestQuery):
        self.requests_queue.put_nowait(query_task)

    def run(self):
        while True:
            request = self.requests_queue.get()
            try:
                request.result = self.api.search(
                        request.query_text,
                        limit=1,
                        type=request.query_data_type
                )[request.query_data_type + 's']['items'][0]
            except Exception as e:
                request.bad = True
                request.result = None
                logger.warning(f'\"{request.query_text}\" not found or found with errors.')
                logger.debug(e)
            request.completed = True
            self.manager.append_completed_query_task(request)
