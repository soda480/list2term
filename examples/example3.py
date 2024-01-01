import asyncio
import random
from faker import Faker
from list2term import Lines

async def do_work(worker, lines):
    total = random.randint(10, 65)
    for _ in range(total):
        # mimic an IO-bound process
        await asyncio.sleep(random.choice([.05, .1, .025]))
        lines[worker] = f'processed {Faker().name()}'
    return total

async def run(workers):
    with Lines(size=workers) as lines:
        return await asyncio.gather(*(do_work(worker, lines) for worker in range(workers)))

def main():
    workers = 15
    print(f'Total of {workers} workers working concurrently')
    results = asyncio.run(run(workers))
    print(f'The {workers} workers processed a total of {sum(results)} items')

if __name__ == '__main__':
    main()