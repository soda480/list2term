# list2term
[![build](https://github.com/soda480/list2term/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/soda480/list2term/actions/workflows/main.yml)
[![coverage](https://img.shields.io/badge/coverage-92%25-brightgreen)](https://pybuilder.io/)
[![vulnerabilities](https://img.shields.io/badge/vulnerabilities-None-brightgreen)](https://pypi.org/project/bandit/)
[![PyPI version](https://badge.fury.io/py/list2term.svg)](https://badge.fury.io/py/list2term)
[![python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-teal)](https://www.python.org/downloads/)

The `list2term` module provides a convenient way to mirror a list to the terminal and helper methods to display messages from concurrent [asyncio](https://docs.python.org/3/library/asyncio.html) or [multiprocessing Pool](https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.Pool) processes. The `list2term.Lines` class is a subclass of [collections.UserList](https://docs.python.org/3/library/collections.html#collections.UserList) and is tty aware thus it can be safely used in non-tty environments. This class takes a list instance as an argument and when instantiated is accessible via the data attribute. The list can be any iterable, but its elements need to be printable; they should implement __str__ function. The intent of this class is to display relatively small lists to the terminal and dynamically update the terminal when list elements are upated, added or removed. Thus it is able to mirror a List of objects to the terminal.

## Installation
```bash
pip install list2term
```

## `Lines`

```
Lines(
    data=None,
    size=None,
    lookup=None,
    show_index=True,
    show_x_axis=True,
    max_chars=None,
    use_color=True)
```

<details><summary>Documentation</summary>

**Parameters**

> `data` - A list of items to mirror to the terminal.

> `size` - An integer designating the size of the initial list - each list item will be initialized to empty string. This parameter should not be used if providing a list of items using the `data` parameter. 

> `lookup` - A list containing unique identifiers that will be used to determine the index of the line to update when using the `write` method. This parameter should only be used when using `list2term` to print messages from background processes running in a multiprocessing pool. The size of the lookup list should be the same size as the `data` list or `size` if provided.

> `show_index` - A boolean to designate if the index for each list item is to be printed, default is True.

> `show_x_axis` - A boolean to designate if the X-axis is to be printed, default is False.

> `max_chars` - An integer designating the maximum length of any list item, if any item is longer than max_chars then the excess will be cut off and the last three digits will be replaced with '...', default is 150.

> `use_color` - A boolean to designate if each list index should be printed with color, default is True.

**Attributes**

> `data` - A real list object containing the contents of the `Lines` class.

**Functions**

> **write(str)**
>> Update appropriate line with the message contained within str. The str must be of the format `{identity}->{message}`. The index of the line to update is determined by extracting the identity contained within str, then returning the index of the identity from the `lookup` list provided to the `Lines` contructor. 

</details>

### Display list [example1](https://github.com/soda480/list2term/blob/main/examples/example1.py)

Start with a list of 15 items containing random sentences, then update sentences at random indexes. As items in the list are updated the respective line in the terminal is updated to show the current contents of the list.

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

### Display list of dynamic size [example2](https://github.com/soda480/list2term/blob/main/examples/example2.py)

Start with a list of 10 items containing random sentences, then add sentences to the list, update existing sentences or remove items from the list at random indexes. As items in the list are added, updated, and removed the respective line in the terminal is updated to show the current contents of the list.

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

### Display messages from `asyncio` processes [example3](https://github.com/soda480/pypbars/blob/main/examples/example3.py)

This example demonstrates how `list2term` can be used to display messages from asyncio processes to the terminal. Each item of the list represents a asnycio process.

<details><summary>Code</summary>

```Python
import asyncio
import random
from faker import Faker
from list2term import Lines

async def do_work(worker, lines):
    total = random.randint(10, 65)
    for _ in range(total):
        # mimic an IO-bound process
        await asyncio.sleep(random.choice([.05, .1, .15]))
        lines[worker] = f'processed {Faker().name()}'
    return total

async def run(workers):
    with Lines(size=workers) as lines:
        return await asyncio.gather(*(do_work(worker, lines) for worker in range(workers)))

def main():
    workers = 12
    print(f'Total of {workers} workers working concurrently')
    results = asyncio.run(run(workers))
    print(f'The {workers} workers processed a total of {sum(results)} items')

if __name__ == '__main__':
    main()
```

</details>

![example3](https://raw.githubusercontent.com/soda480/list2term/main/docs/images/example3.gif)


### Display messages from multiprocessing pool processes [example4](https://github.com/soda480/list2term/blob/main/examples/example4.py)

This example demonstrates how `list2term` can be used to display messages from processes executing in a [multiprocessing Pool](https://docs.python.org/3/library/multiprocessing.html#using-a-pool-of-workers). Each item of the list represents a background process. The `list2term.multiprocessing` module contains a `pool_map` method that fully abstracts the required multiprocessing constructs, you simply pass it the function to execute, an iterable of arguments to pass each process, and an optional instance of `Lines`. The method will execute the functions asynchronously, update the terminal lines accordingly and return a multiprocessing.pool.AsyncResult object. Each line in the terminal represents a background worker process.

If you do not wish to use the abstraction, the `list2term.multiprocessing` module contains helper classes that facilitates communication between the worker processes and the main process; the `QueueManager` provide a way to create a `LinesQueue` queue which can be shared between different processes. Refer to [example4b](https://github.com/soda480/list2term/blob/main/examples/example4b.py) for how the helper methods can be used.

**Note** the function being executed must accept a `LinesQueue` object that is used to write messages via its `write` method, this is the mechanism for how messages are sent from the worker processes to the main process, it is the main process that is displaying the messages to the terminal. The messages must be written using the format `{identifier}->{message}`, where {identifier} is a string that uniquely identifies a process, defined via the lookup argument to `Lines`.

<details><summary>Code</summary>

```Python
import time
from list2term import Lines
from list2term.multiprocessing import pool_map
from list2term.multiprocessing import CONCURRENCY

def is_prime(num):
    if num == 1:
        return False
    for i in range(2, num):
        if (num % i) == 0:
            return False
    else:
        return True

def count_primes(start, stop, logger):
    worker_id = f'{start}:{stop}'
    primes = 0
    for number in range(start, stop):
        if is_prime(number):
            primes += 1
            logger.write(f'{worker_id}->{worker_id} {number} is prime')
    logger.write(f'{worker_id}->{worker_id} processing complete')
    return primes

def main(number):
    step = int(number / CONCURRENCY)
    print(f"Distributing {int(number / step)} ranges across {CONCURRENCY} workers running concurrently")
    iterable = [(index, index + step) for index in range(0, number, step)]
    lookup = [':'.join(map(str, item)) for item in iterable]
    # print to screen with lines context
    results = pool_map(count_primes, iterable, context=Lines(lookup=lookup))
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


### Other examples

A Conway [Game-Of-Life](https://github.com/soda480/game-of-life) implementation that uses `list2term` to display game to the terminal.


## Development

Clone the repository and ensure the latest version of Docker is installed on your development server.

Build the Docker image:
```sh
docker image build \
-t list2term:latest .
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
