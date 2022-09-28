import os
import re
import sys
import logging
from collections import UserList
from colorama import init as colorama_init
from colorama import Style
from colorama import Fore
from colorama import Cursor
import cursor

logger = logging.getLogger(__name__)

MAX_CHARS = 150
CLEAR_EOL = '\033[K'
BRIGHT_YELLOW = Style.BRIGHT + Fore.YELLOW


class Lines(UserList):

    def __init__(self, data=None, size=None, lookup=None, show_index=True, show_x_axis=False, max_chars=None, use_color=True):
        """ constructor
        """
        logger.debug('executing Lines constructor')
        data = Lines._get_data(data, size, lookup)
        Lines._validate_lookup(lookup, data)
        Lines._validate_data(data)
        super().__init__(initlist=data)
        self._max_chars = max_chars if max_chars else MAX_CHARS
        self._fill = len(str(len(self.data)))
        self._current = 0
        self._show_index = show_index
        self._show_x_axis = show_x_axis
        self._lookup = lookup
        self._use_color = use_color
        colorama_init()

    def __enter__(self):
        """ on entry hide cursor if stderr is attached to tty
        """
        self.hide_cursor()
        self.print_x_axis(force=True)
        self.print_lines(force=True)
        return self

    def __exit__(self, *args):
        """ on exit show cursor if stderr is attached to tty and print items
        """
        self.print_lines(force=True)
        self.show_cursor()

    def __setitem__(self, index, item):
        """ set item override
        """
        super().__setitem__(index, item)
        self.print_line(index)

    def __delitem__(self, index):
        """ delete item override
        """
        original_len = len(self.data)
        super().__delitem__(index)
        if isinstance(index, int):
            # clear last line
            self._clear_line(original_len - 1)
            start = index if index > 0 else None
            self.print_lines(start)
        else:
            # for number in range(index.stop, original_len):
            #    self._clear_line(number)
            # self.print_lines(index.start)
            raise NotImplementedError('deleting slices is not supported')

    def append(self, item):
        """ append override
        """
        # need to add some validation here
        super().append(item)
        self.print_lines()

    def pop(self, index=-1):
        """ pop override
        """
        super().pop(index)
        # clear supposed last line in terminal
        self._clear_line(len(self.data))
        start = index if index > 0 else None
        self.print_lines(start)

    def remove(self, item):
        """ remove override
        """
        raise NotImplementedError('remove is not supported')

    def clear(self):
        """ clear override
        """
        original_len = len(self.data)
        self.data.clear()
        for number in range(0, original_len):
            self._clear_line(number)

    def _clear_line(self, index):
        """ clear line at index
        """
        if sys.stderr.isatty():
            move_char = self._get_move_char(index)
            print(f'{move_char}{CLEAR_EOL}', end='', file=sys.stderr)

    def print_line(self, index, force=False):
        """ move to index and print item at index
        """
        if sys.stderr.isatty() or force:
            str_index = ''
            if self._show_index:
                if self._use_color:
                    str_index = f"{BRIGHT_YELLOW}{str(index).zfill(self._fill)}{Style.RESET_ALL}: "
                else:
                    str_index = f"{str(index).zfill(self._fill)}: "

            move_char = self._get_move_char(index)
            print(f'{move_char}{CLEAR_EOL}', end='', file=sys.stderr)
            sanitized = self._sanitize(self.data[index])
            print(f'{str_index}{sanitized}', file=sys.stderr)
            sys.stderr.flush()
            self._current += 1

    def print_x_axis(self, force=False):
        """ print x axis when set
        """
        if (sys.stderr.isatty() or force) and self._show_x_axis:
            x_axis = ''.join([str(round(i / 10))[-1] if i % 10 == 0 else '.' for i in range(self._max_chars)])
            spaces = ' ' * 4 if self._show_index else ''
            if self._use_color:
                print(f"{spaces}{BRIGHT_YELLOW}{x_axis}{Style.RESET_ALL}", file=sys.stderr)
            else:
                print(f"{spaces}{x_axis}", file=sys.stderr)

    def print_lines(self, force=False, from_index=None):
        """ print all items
        """
        if from_index is None:
            from_index = 0
        logger.info(f'printing all items starting at index {from_index}')
        for index, _ in enumerate(self.data[from_index:], from_index):
            self.print_line(index, force=force)

    def _get_move_char(self, index):
        """ return char to move to index
        """
        move_char = ''
        if index < self._current:
            move_char = self._move_up(index)
        elif index > self._current:
            move_char = self._move_down(index)
        return move_char

    def _move_down(self, index):
        """ return char to move down to index and update current
        """
        diff = index - self._current
        self._current += diff
        return Cursor.DOWN(diff)

    def _move_up(self, index):
        """ return char to move up to index and update current
        """
        diff = self._current - index
        self._current -= diff
        return Cursor.UP(diff)

    def show_cursor(self):
        """ show cursor
        """
        if sys.stderr.isatty():
            cursor.show()

    def hide_cursor(self):
        """ hide cursor
        """
        if sys.stderr.isatty():
            cursor.hide()

    def _sanitize(self, item):
        """ sanitize item
        """
        if type(item).__str__ is not object.__str__:
            # if item has __str__ that is not from object then call it
            item = str(item)
        if isinstance(item, str):
            item = item.split('\n')[0]
            if len(item) > self._max_chars:
                item = f'{item[0:self._max_chars - 3]}...'
        else:
            item = ''.join(i for i in item)
        return item

    def get_index_message(self, item):
        """ return index and message contained within item
        """
        if self._lookup:
            # possible future enhancement is for caller to specify regex of item
            regex = r'^(?P<identity>.*)->(?P<message>.*)$'
            match = re.match(regex, item)
            if match:
                identity = match.group('identity').strip()
                try:
                    index = self._lookup.index(identity)
                except ValueError:
                    index = None
                if index is not None:
                    message = match.group('message').lstrip()
                    return index, message
        return None, item

    def write(self, item):
        """ update appropriate line with message contained within item
            line is determined by extracting the identity contained within item
            the index is determined getting the index of the identity from the lookup table
        """
        index, message = self.get_index_message(item)
        if index is not None:
            if self[index] == message:
                # no need to set value at index if it is already set
                return
            self[index] = message

    @staticmethod
    def _get_data(data, size, lookup):
        """ return data list or generate from size or lookup
        """
        if data:
            return data
        if not size:
            if not lookup:
                raise ValueError('a data, size or lookup attribute must be provided')
            size = len(lookup)
        return [''] * size

    @staticmethod
    def _validate_lookup(lookup, data):
        """ validate lookup list is unique and same length as data
        """
        if lookup:
            if len(set(lookup)) != len(lookup):
                raise ValueError('all elements in lookup must be unique')
            if len(lookup) != len(data):
                raise ValueError('size of lookup must equal size of data')

    @staticmethod
    def _validate_data(data):
        """ validate data list can be displayed on terminal
        """
        if sys.stderr.isatty():
            size = os.get_terminal_size()
            if len(data) > size.lines:
                raise ValueError(f'number of items to display {len(data)} exceeds current terminal lines size {size.lines}')
