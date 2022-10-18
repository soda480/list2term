import logging
from multiprocessing import Pool
from multiprocessing import get_context
from multiprocessing import cpu_count
from multiprocessing.queues import Queue
from multiprocessing.managers import BaseManager
from queue import Empty
from contextlib import nullcontext
from list2term import Lines

logger = logging.getLogger(__name__)
CONCURRENCY = cpu_count()


class LinesQueue(Queue):  # pragma: no cover
    def write(self, *args, **kwargs):
        super().put(*args, **kwargs)


class QueueManager(BaseManager):  # pragma: no cover
    # Managers provide a way to create data which can be shared between different processes
    pass


def pool_map(function, iterable, context=None, print_status=True, processes=None):  # pragma: no cover
    """ multiprocessing helper function to write messages from Pool of processes to terminal
        context is a subclass of list2term.Lines
        returns multiprocessing.pool.AsyncResult
    """
    if not processes:
        processes = CONCURRENCY
    if not (0 < processes <= CONCURRENCY):
        raise ValueError(f'processes must be greater than 0 and less than equal to available cores {CONCURRENCY}')
    QueueManager.register('LinesQueue', LinesQueue)
    with QueueManager() as manager:
        lines_queue = manager.LinesQueue(ctx=get_context())
        with Pool(processes) as pool:
            # add lines_queue to each process arguments list
            # the function should write status messages to the queue
            process_data = [item + (lines_queue,) for item in iterable]
            # start process pool asynchronously
            results = pool.starmap_async(function, process_data)
            if not context:
                context = nullcontext()
            with context as lines:
                while True:
                    try:
                        item = lines_queue.get(timeout=.1)
                        if lines:
                            lines.write(item)
                        else:
                            if print_status:
                                print(item)
                    except Empty:
                        if results.ready():
                            break
    return results
