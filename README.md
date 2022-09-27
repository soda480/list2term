# list2term
[![build](https://github.com/soda480/list2term/actions/workflows/main.yml/badge.svg)](https://github.com/soda480/list2term/actions/workflows/main.yml)
[![Code Grade](https://api.codiga.io/project/33832/status/svg)](https://app.codiga.io/public/project/33832/mppbar/dashboard)
[![codecov](https://codecov.io/gh/soda480/list2term/branch/main/graph/badge.svg?token=IYQBFG9J8G)](https://codecov.io/gh/soda480/list2term)
[![vulnerabilities](https://img.shields.io/badge/vulnerabilities-None-brightgreen)](https://pypi.org/project/bandit/)
[![PyPI version](https://badge.fury.io/py/list2term.svg)](https://badge.fury.io/py/list2term)
[![python](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10-teal)](https://www.python.org/downloads/)

The `list2term` module dynamically displays a list to the terminal and provides a convenient way to display messages from concurrent [asyncio](https://docs.python.org/3/library/asyncio.html) or [multiprocessing Pool](https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.Pool) processes. The `list2term.Lines` class is a subclass of [collections.UserList](https://docs.python.org/3/library/collections.html#collections.UserList) and is tty aware thus it is safe to use in non-tty environments. This class takes a list instance as an argument and when instantiated the list is accessible via the data attribute. The list can be any iterable, but its elements need to be printable; they should implement __str__ function. The intent of this class is to display relatively small lists to the terminal and dynamically update the terminal when list elements are upated, added or removed.

### Installation
```bash
pip install list2term
```

#### [example1 - display list of static size](https://github.com/soda480/list2term/blob/main/examples/example1.py)

Initially create an empty list then add sentences to the list at random indexes. As sentences are updated within the list the respective line in the terminal is updated.

<details><summary>Code</summary>

```Python
import time
import random
from faker import Faker
from list2term import Lines

def main():
    print('Generating random sentences...')
    docgen = Faker()
    with Lines(size=15, show_x_axis=True, max_chars=100) as lines:
        for _ in range(200):
            index = random.randint(0, len(lines) - 1)
            lines[index] = docgen.sentence()
            time.sleep(.05)

if __name__ == '__main__':
    main()
```

</details>

![example1](https://raw.githubusercontent.com/soda480/list2term/main/docs/images/example1.gif)

#### [example2 - display list of dynamic size](https://github.com/soda480/list2term/blob/main/examples/example2.py)

Initially create an empty list then add sentences to the list at random indexes. As sentences are updated within the list the respective line in the terminal is updated. Also show how the terminal behaves when items are added to and removed from the list.

<details><summary>Code</summary>

```Python
import time
import random
from faker import Faker
from list2term import Lines

def main():
    print('Generating random sentences...')
    docgen = Faker()
    with Lines(data=[''] * 10, max_chars=100) as lines:
        for _ in range(100):
            index = random.randint(0, len(lines) - 1)
            lines[index] = docgen.sentence()
        for _ in range(100):
            update = ['update'] * 18
            append = ['append'] * 18
            pop = ['pop'] * 14
            clear = ['clear']
            choice = random.choice(append + pop + clear + update)
            if choice == 'pop':
                if len(lines) > 0:
                    index = random.randint(0, len(lines) - 1)
                    lines.pop(index)
            elif choice == 'append':
                lines.append(docgen.sentence())
            elif choice == 'update':
                if len(lines) > 0:
                    index = random.randint(0, len(lines) - 1)
                    lines[index] = docgen.sentence()
            else:
                if len(lines) > 0:
                    lines.pop()
                if len(lines) > 0:
                    lines.pop()
            time.sleep(.1)

if __name__ == '__main__':
    main()
```

</details>

![example2](https://raw.githubusercontent.com/soda480/list2term/main/docs/images/example2.gif)

#### [example3 - display messages from asyncio processes](https://github.com/soda480/pypbars/blob/main/examples/example3.py)

This example demonstrates how `list2term` can be used to display messages from asyncio processes.

<details><summary>Code</summary>

```Python
import asyncio
import random
import uuid
from faker import Faker
from list2term import Lines

async def do_work(worker, logger=None):
    logger.write(f'{worker}->worker is {worker}')
    total = random.randint(10, 65)
    logger.write(f'{worker}->{worker}processing total of {total} items')
    for _ in range(total):
        # mimic an IO-bound process
        await asyncio.sleep(random.choice([.05, .1, .15]))
        logger.write(f'{worker}->processed {Faker().name()}')
    return total

async def run(workers):
    with Lines(lookup=workers, use_color=True) as logger:
        doers = (do_work(worker, logger=logger) for worker in workers)
        return await asyncio.gather(*doers)

def main():
    workers = [Faker().user_name() for _ in range(12)]
    print(f'Total of {len(workers)} workers working concurrently')
    results = asyncio.run(run(workers))
    print(f'The {len(workers)} workers processed a total of {sum(results)} items')

if __name__ == '__main__':
    main()
```

</details>

![example3](https://raw.githubusercontent.com/soda480/list2term/main/docs/images/example3.gif)


#### [example4 - display messages from multiprocessing Pool processes](https://github.com/soda480/list2term/blob/main/examples/example4.py)

This example demonstrates how `list2term` can be used to display messages from processes executing in a [multiprocessing Pool](https://docs.python.org/3/library/multiprocessing.html#using-a-pool-of-workers). The `list2term.multiprocessing` module contains helper classes that define a `LinesQueue` as well as a `QueueManager` to facilitate communication between worker processes and the main process. In this example, we leverage a Pool of workers to compute the number of prime numbers in a given number range. The worker processes are passed a queue that they write messages to, meanwhile the main process reads messages from the queue, interprets the message and writes them to `Lines`. Note that each line represents a single background worker process.

<details><summary>Code</summary>

```Python
import time
from multiprocessing import Pool
from multiprocessing import get_context
from multiprocessing import cpu_count
from queue import Empty
from list2term.multiprocessing import LinesQueue
from list2term.multiprocessing import QueueManager
from list2term import Lines

CONCURRENCY = cpu_count()

def is_prime(num):
    if num == 1:
        return False
    for i in range(2, num):
        if (num % i) == 0:
            return False
    else:
        return True

def count_primes(start, stop, logger):
    workerid = f'{start}:{stop}'
    logger.write(f'{workerid}->processing total of {stop - start} items')
    primes = 0
    for number in range(start, stop):
        if is_prime(number):
            primes += 1
            logger.write(f'{workerid}->{workerid} {number} is prime')
    logger.write(f'{workerid}->{workerid} processing complete')
    return primes

def main(number):
    step = int(number / CONCURRENCY)
    QueueManager.register('LinesQueue', LinesQueue)
    with QueueManager() as manager:
        queue = manager.LinesQueue(ctx=get_context())
        with Pool(CONCURRENCY) as pool:
            process_data = [(index, index + step, queue) for index in range(0, number, step)]
            results = pool.starmap_async(count_primes, process_data)
            lookup = [f'{data[0]}:{data[1]}' for data in process_data]
            with Lines(lookup=lookup, use_color=True) as lines:
                while True:
                    try:
                        lines.write(queue.get(timeout=.1))
                    except Empty:
                        if results.ready():
                            break
    return sum(results.get())

if __name__ == '__main__':
    start = time.perf_counter()
    number = 100_000
    result = main(number)
    stop = time.perf_counter()
    print(f"Finished in {round(stop - start, 2)} seconds\nTotal number of primes between 0-{number}: {result}")
```

</details>

![example4](https://raw.githubusercontent.com/soda480/list2term/main/docs/images/example4.gif)


#### Example5

A Conway [Game-Of-Life](https://github.com/soda480/game-of-life) implementation that uses `list2term` to display game to the terminal.


### Development

Clone the repository and ensure the latest version of Docker is installed on your development server.

Build the Docker image:
```sh
docker image build \
-t \
list2term:latest .
```

Run the Docker container:
```sh
docker container run \
--rm \
-it \
-v $PWD:/code \
list2term:latest \
bash
```

Execute the build:
```sh
pyb -X
```
