import concurrent.futures
import time
import random
import threading
from faker import Faker
from concurrent.futures import ThreadPoolExecutor, as_completed
from list2term import Lines

def task(item, lines):
    thread_name = threading.current_thread().name
    lines.write(f'{thread_name}->{thread_name}: {item}_{Faker().name()}')
    seconds = random.uniform(.04, .3)
    time.sleep(seconds)
    return seconds

def main():
    items = 500
    num_threads = 10
    thread_name_prefix = 'thread'
    with ThreadPoolExecutor(max_workers=num_threads, thread_name_prefix=thread_name_prefix) as executor:
        lookup = [f'{thread_name_prefix}_{index}' for index in range(num_threads)]
        with Lines(lookup=lookup) as lines:
            futures = [executor.submit(task, item, lines) for item in range(items)]
            return [future.result() for future in futures]

if __name__ == "__main__":
    main()
