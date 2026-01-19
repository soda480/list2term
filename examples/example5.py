import time
import random
import threading
from faker import Faker
from concurrent.futures import ThreadPoolExecutor
from list2term import Lines

def process_item(item, lines):
    thread_name = threading.current_thread().name
    lines.write(f'{Faker().name()} processed item {item}', line_id=thread_name)
    seconds = random.uniform(.04, .3)
    time.sleep(seconds)
    return seconds

def main():
    items = 250
    num_threads = 10
    with ThreadPoolExecutor(max_workers=num_threads, thread_name_prefix='thread') as executor:
        lookup = [f'thread_{index}' for index in range(num_threads)]
        with Lines(lookup=lookup, y_axis_labels=lookup) as lines:
            futures = [executor.submit(process_item, item, lines) for item in range(items)]
            return [future.result() for future in futures]

if __name__ == "__main__":
    main()

