import os
import re
import sys
import cursor
import logging
import threading
from collections import UserList
from colorama import init as colorama_init
from colorama import Style
from colorama import Fore
from colorama import Cursor

logger = logging.getLogger(__name__)

MAX_CHARS = 150
CLEAR_EOL = '\033[K'
BRIGHT_YELLOW = Style.BRIGHT + Fore.YELLOW
LINE_RE = re.compile(r'^(?P<line_id>.*)->(?P<message>.*)$')


class Lines(UserList):

    def __init__(self, data=None, size=None, lookup=None, show_index=True, show_x_axis=False,
                 max_chars=None, use_color=True, y_axis_labels=None, x_axis=None):
        """ constructor
        """
        logger.debug('executing Lines constructor')
        self._isatty = sys.stderr.isatty()
        if not self._isatty:
            print(
                'the error stream is not attached to terminal/tty '
                'device: lines will be printed on context manager '
                'exit only',
                file=sys.stderr
            )
            sys.stderr.flush()
        data = Lines._get_data(data, size, lookup)
        Lines._validate_lookup(lookup, data)
        Lines._validate_data(data, self._isatty)
        super().__init__(initlist=data)
        self._max_chars = max_chars if max_chars else MAX_CHARS
        self._fill = len(str(len(self.data) - 1))
        self._current = 0
        self._show_index = show_index
        self._show_x_axis = show_x_axis
        self._lookup = lookup
        self._lookup_map = {key: index for index, key in enumerate(lookup)} if lookup else None
        self._use_color = use_color
        if y_axis_labels and len(y_axis_labels) != len(self.data):
            raise ValueError('size of y_axis_labels must equal size of data')
        self._y_axis_labels = y_axis_labels
        self._y_axis_labels_max_len = (
            Lines.max_len(y_axis_labels)
            if y_axis_labels
            else len(str(len(self.data) - 1))
        )
        self._x_axis = x_axis
        colorama_init()
        self._lock = threading.Lock()

    def __enter__(self):
        """ on entry hide cursor if stderr is attached to tty
        """
        self._hide_cursor()
        self._print_x_axis(force=True)
        self._print_lines(force=False)
        return self

    def __exit__(self, *args):
        """ on exit show cursor if stderr is attached to tty and print items
        """
        self._print_lines(force=True)
        self._show_cursor()

    def __setitem__(self, index, item):
        """ set item override
        """
        self.data[index] = item
        self._print_line(index)

    def __delitem__(self, index):
        """ delete item override
        """
        length = len(self.data)
        del self.data[index]
        if isinstance(index, int):
            # clear last line
            self._clear_line(length - 1)
            start = index if index > 0 else None
            self._print_lines(from_index=start)
        else:
            raise NotImplementedError('deleting slices is not supported')

    def append(self, item):
        """ append override
        """
        # need to add validation here
        self.data.append(item)
        self._print_lines()

    def pop(self, index=-1):
        """ pop override
        """
        self.data.pop(index)
        # clear supposed last line in terminal
        self._clear_line(len(self.data))
        start = index if index > 0 else None
        self._print_lines(from_index=start)

    def remove(self, item):
        """ remove override
        """
        raise NotImplementedError('remove is not supported')

    def clear(self):
        """ clear override
        """
        length = len(self.data)
        self.data.clear()
        if self._isatty:
            for index in range(0, length):
                self._clear_line(index)

    def _clear_line(self, index):
        """ clear line at index
        """
        if self._isatty:
            move_char = self._get_move_char(index)
            print(f'{move_char}{CLEAR_EOL}', end='', file=sys.stderr)

    def _print_line(self, index, force=False):
        """ move to index and print item at index
        """
        if self._isatty or force:
            with self._lock:
                # ensure single thread access
                move_char = self._get_move_char(index)
                print(f'{move_char}{CLEAR_EOL}', end='', file=sys.stderr)
                sanitized = self._sanitize(self.data[index])
                str_index = self._get_str_index(index)
                print(f'{str_index}{sanitized}', file=sys.stderr)
                sys.stderr.flush()
                self._current = index + 1

    def _get_str_index(self, index):
        """ return index with y axis label if set
        """
        if not self._show_index:
            return ''
        if self._y_axis_labels:
            label = self._y_axis_labels[index].rjust(self._y_axis_labels_max_len)
        else:
            label = str(index).zfill(self._fill)
        if not self._use_color:
            return f'{label}: '
        return f'{BRIGHT_YELLOW}{label}{Style.RESET_ALL}: '

    def _print_x_axis(self, force=False):
        """ print x axis when set (supports single string or list of strings)
        """
        if (self._isatty or force) and self._show_x_axis:
            if isinstance(self._x_axis, list):
                x_axis_lines = self._x_axis
            elif self._x_axis:
                x_axis_lines = [self._x_axis]
            else:
                x_axis_lines = [
                    ''.join(
                        str(round(i / 10))[-1] if i % 10 == 0 else '.'
                        for i in range(self._max_chars)
                    )
                ]

            # add padding for y axis labels the + 2 is for ': '
            spaces = (
                ' ' * (self._y_axis_labels_max_len + 2)
                if self._show_index else ''
            )

            for x_axis in x_axis_lines:
                if self._use_color:
                    print(
                        f"{spaces}{BRIGHT_YELLOW}{x_axis}{Style.RESET_ALL}",
                        file=sys.stderr
                    )
                else:
                    print(f"{spaces}{x_axis}", file=sys.stderr)

    def _print_lines(self, force=False, from_index=None):
        """ print all items
        """
        if from_index is None:
            from_index = 0
        logger.debug('printing all items starting at index %s', from_index)
        if (self._isatty or force):
            for index, _ in enumerate(self.data[from_index:], from_index):
                self._print_line(index, force=force)

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

    def _show_cursor(self):
        """ show cursor
        """
        if self._isatty:
            cursor.show()

    def _hide_cursor(self):
        """ hide cursor
        """
        if self._isatty:
            cursor.hide()

    def _sanitize(self, item):
        """ sanitize item for terminal display.

            Supports:
            - str
            - list/tuple of parts (e.g. ['foo', Fore.RED, 'bar'])
            - other objects via str()
            Truncates to max_chars and strips after first newline.
        """
        if item is None:
            s = ''
        elif isinstance(item, str):
            s = item
        elif isinstance(item, (list, tuple)):
            # join parts safely (preserves ANSI sequences if present)
            s = ''.join('' if part is None else str(part) for part in item)
        else:
            # fallback: try to string-ify
            s = str(item)

        # keep first line only
        s = s.split('\n', 1)[0]

        # truncate (raw length; if you later re-add ANSI-aware truncation, swap here)
        if len(s) > self._max_chars:
            s = f'{s[:self._max_chars - 3]}...'

        return s

    def _get_index_message(self, item, line_id=None):
        """ return index and message contained within item
        """
        index = None
        message = item
        if self._lookup:
            if not line_id:
                match = LINE_RE.match(item)
                if match:
                    line_id = match.group('line_id').strip()
                    index = self._lookup_map.get(line_id)
                    if index is not None:
                        message = match.group('message').lstrip()
            else:
                index = next((i for i, x in enumerate(self._lookup) if x == line_id), None)
        return index, message

    def write(self, item, line_id=None):
        """ update appropriate line with message contained within item
            the index of the line to update is determined by:
                the index of line_id within lookup
                extracting line_id contained within item
        """
        index, message = self._get_index_message(item, line_id=line_id)
        if index is not None:
            if self[index] != message:
                # no need to set value at index if it is already set
                self[index] = message

    @staticmethod
    def _get_data(data, size, lookup):
        """ return data list or generate from size or lookup
        """
        if data:
            return data
        if size:
            return [''] * size
        if lookup:
            return [''] * len(lookup)
        raise ValueError('a data, size or lookup attribute must be provided')

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
    def _validate_data(data, isatty):
        """ validate data list can be displayed on terminal
        """
        if isatty:
            size = os.get_terminal_size()
            if len(data) > size.lines:
                raise ValueError(
                    f'number of items to display {len(data)} '
                    f'exceeds current terminal lines size {size.lines}'
                )

    @staticmethod
    def max_len(items):
        """ return the length of the longest item in a list
        """
        if not items:
            return 0
        return max(len(i) for i in items)
