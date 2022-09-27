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