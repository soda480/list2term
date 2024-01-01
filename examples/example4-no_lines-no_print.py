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
    # do not use Lines context and do not print messages from processes to stderr
    results = pool_map(count_primes, iterable, print_status=False)
    return sum(results.get())

if __name__ == '__main__':
    start = time.perf_counter()
    number = 100_000
    result = main(number)
    stop = time.perf_counter()
    print(f"Finished in {round(stop - start, 2)} seconds\nTotal number of primes between 0-{number}: {result}")
