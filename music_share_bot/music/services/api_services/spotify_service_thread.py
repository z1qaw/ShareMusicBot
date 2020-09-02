import threading
from queue import LifoQueue

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import telebot

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
                request.result = None
                # logger.exception(e)
                request.bad = True
            request.completed = True
            self.manager.append_completed_query_task(request)
