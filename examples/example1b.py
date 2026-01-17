import time
import random
from faker import Faker
from list2term import Lines

def main():
    print('Generating random sentences...')
    docgen = Faker()
    labels = [docgen.first_name() for _ in range(15)]
    # x_axis = ['0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1', 
    #           '0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5']
    x_axis = '00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15'
    with Lines(size=15, show_x_axis=True, max_chars=100, y_axis_labels=labels, x_axis=x_axis) as lines:
        for _ in range(200):
            index = random.randint(0, len(lines) - 1)
            lines[index] = docgen.sentence()
            time.sleep(.02)

if __name__ == '__main__':
    main()
