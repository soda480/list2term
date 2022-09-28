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
    pass


def lines(function, iterable, lookup=None, **kwargs):  # pragma: no cover
    """ multiprocessing enabled helper function to display messages from Pool of processes to terminal
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
            if not lookup:
                # create lookup list consisting of colon-delimeted string of iterable arguments
                lookup = [':'.join(map(str, item)) for item in iterable]
            # display messages from pool processes to the terminal using Lines
            # read message from lines queue and write it to the respective line on the terminal
            with Lines(lookup=lookup, **kwargs) as terminal_lines:
                while True:
                    try:
                        terminal_lines.write(lines_queue.get(timeout=.1))
                    except Empty:
                        if results.ready():
                            break
    return results
