import threading
from queue import LifoQueue

import telebot

from ...api.yandex_music.api import YandexMusicApi
from .manager_data import ServiceDataRequestQuery

logger = telebot.logger


class YandexMusicServiceThread(threading.Thread):
    def __init__(self, manager, session):
        super().__init__()
        self.manager = manager
        self.api = YandexMusicApi(session)
        self.requests_queue = LifoQueue()

    def append_search_query_task(self, query_task: ServiceDataRequestQuery):
        self.requests_queue.put_nowait(query_task)

    def run(self):
        while True:
            request = self.requests_queue.get()
            
            try:
                result = self.api.search(
                        request.query_text,
                        object_type=request.query_data_type + 's',
                        lang='en'
                )
                request.result = getattr(result, request.query_data_type + 's').items[0]
            except Exception as e:
                logger.exception(e)
                request.result = None
                request.bad = True
            request.completed = True
            self.manager.append_completed_query_task(request)
