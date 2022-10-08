import logging
from multiprocessing import Pool
from multiprocessing import get_context
from multiprocessing import cpu_count
from multiprocessing.queues import Queue
from multiprocessing.managers import BaseManager
from queue import Empty
from list2term import Lines

logger = logging.getLogger(__name__)
CONCURRENCY = cpu_count()


class LinesQueue(Queue):  # pragma: no cover
    def write(self, *args, **kwargs):
        super().put(*args, **kwargs)


class QueueManager(BaseManager):  # pragma: no cover
    # Managers provide a way to create data which can be shared between different processes
    pass


def pool_with_queue(function, iterable, context_manager):  # pragma: no cover
    """ multiprocessing helper function to write messages from Pool of processes to terminal
        context_manager is a subclass of list2term.Lines
        returns multiprocessing.pool.AsyncResult
    """
    QueueManager.register('LinesQueue', LinesQueue)
    with QueueManager() as manager:
        lines_queue = manager.LinesQueue(ctx=get_context())
        with Pool(CONCURRENCY) as pool:
            # add lines_queue to each process arguments list
            # the function should write status messages to the queue
            process_data = [item + (lines_queue,) for item in iterable]
            # start process pool asynchronously
            results = pool.starmap_async(function, process_data)
            # write messages from pool processes to the terminal using context_manager
            with context_manager as lines:
                while True:
                    try:
                        lines.write(lines_queue.get(timeout=.1))
                    except Empty:
                        if results.ready():
                            break
    return results
