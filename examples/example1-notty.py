import time
import random
from faker import Faker
from list2term import Lines
from mock import patch

def main():
    print('Generating random sentences...')   
    docgen = Faker()
    with Lines(size=15, show_x_axis=True, max_chars=100) as lines:
        for _ in range(200):
            index = random.randint(0, len(lines) - 1)
            lines[index] = docgen.sentence()
            time.sleep(.02)

if __name__ == '__main__':
    with patch('sys.stderr.isatty', return_value=False):
        main()
