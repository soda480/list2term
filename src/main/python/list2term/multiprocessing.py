import logging
from multiprocessing.queues import Queue
from multiprocessing.managers import BaseManager
from queue import Empty
from list2term import Lines

logger = logging.getLogger(__name__)


class LinesQueue(Queue):  # pragma: no cover
    def write(self, *args, **kwargs):
        super().put(*args, **kwargs)


class QueueManager(BaseManager):  # pragma: no cover
    pass
