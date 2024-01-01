import unittest
from mock import patch
from mock import call
from mock import Mock
from list2term import Lines
from list2term.list2term import MAX_CHARS


class TestLines(unittest.TestCase):

    @patch('list2term.Lines._validate_data')
    @patch('list2term.Lines._move_up')
    def test__get_move_char_Should_ReturnExpected_When_MovingUp(self, move_up_patch, *patches):
        lines = Lines(size=13)
        lines._current = 12
        result = lines._get_move_char(7)
        self.assertEqual(result, move_up_patch.return_value)

    @patch('list2term.Lines._validate_data')
    @patch('list2term.Lines._move_down')
    def test__get_move_char_Should_ReturnExpected_When_MovingDown(self, move_down_patch, *patches):
        lines = Lines(size=13)
        lines._current = 2
        result = lines._get_move_char(7)
        self.assertEqual(result, move_down_patch.return_value)

    @patch('list2term.Lines._validate_data')
    @patch('list2term.Lines._move_down')
    def test__get_move_char_Should_ReturnExpected_When_NotMoving(self, move_down_patch, *patches):
        lines = Lines(size=13)
        lines._current = 2
        result = lines._get_move_char(2)
        self.assertEqual(result, '')

    @patch('list2term.Lines._validate_data')
    @patch('list2term.Lines._validate_data')
    @patch('list2term.list2term.Cursor.DOWN')
    def test__move_down_Should_CallExpected_When_Called(self, down_patch, *patches):
        lines = Lines(size=13)
        lines._current = 2
        result = lines._move_down(7)
        self.assertEqual(result, down_patch.return_value)
        self.assertEqual(lines._current, 7)

    @patch('list2term.Lines._validate_data')
    @patch('list2term.list2term.Cursor.UP')
    def test__move_up_Should_ReturnExpected_When_Called(self, up_patch, *patches):
        lines = Lines(size=13)
        lines._current = 12
        result = lines._move_up(7)
        self.assertEqual(result, up_patch.return_value)
        self.assertEqual(lines._current, 7)

    @patch('list2term.Lines._validate_data')
    @patch('list2term.list2term.sys.stderr')
    @patch('list2term.list2term.cursor')
    def test__hide_cursor_Should_CallHideCursor_When_Tty(self, cursor_patch, stderr_patch, *patches):
        stderr_patch.isatty.return_value = True
        lines = Lines(size=3)
        lines._hide_cursor()
        cursor_patch.hide.assert_called_once_with()

    @patch('list2term.list2term.sys.stderr')
    @patch('list2term.list2term.cursor')
    def test__hide_cursor_Should_CallHideCursor_When_NoTty(self, cursor_patch, stderr_patch, *patches):
        stderr_patch.isatty.return_value = False
        lines = Lines(size=3)
        lines._hide_cursor()
        cursor_patch.hide.assert_not_called()

    @patch('list2term.Lines._validate_data')
    @patch('list2term.list2term.sys.stderr')
    @patch('list2term.list2term.cursor')
    def test__show_cursor_Should_CallShowCursor_When_Tty(self, cursor_patch, stderr_patch, *patches):
        stderr_patch.isatty.return_value = True
        lines = Lines(size=3)
        lines._show_cursor()
        cursor_patch.show.assert_called_once_with()

    @patch('list2term.list2term.sys.stderr')
    @patch('list2term.list2term.cursor')
    def test__show_cursor_Should_NotCallShowCursor_When_NoTty(self, cursor_patch, stderr_patch, *patches):
        stderr_patch.isatty.return_value = False
        lines = Lines(size=3)
        lines._show_cursor()
        cursor_patch.show.assert_not_called()

    @patch('list2term.Lines._validate_data')
    @patch('list2term.Lines._print_lines')
    @patch('list2term.Lines._hide_cursor')
    @patch('list2term.Lines._show_cursor')
    def test__enter_exit_Should_HideAndShowCursorAndPrintLines_When_Called(self, show_cursor_patch, hide_cursor_patch, print_lines_patch, *patches):
        with Lines(size=3):
            hide_cursor_patch.assert_called_once_with()
            print_lines_patch.assert_called_once_with(force=False)
        show_cursor_patch.assert_called_once_with()

    @patch('list2term.Lines._validate_data')
    @patch('list2term.Lines._print_line')
    def test__set_item_Should_CallPrintLine_When_Called(self, print_line_patch, *patches):
        lines = Lines(size=3)
        lines[1] = 'hello world'
        print_line_patch.assert_called_once_with(1)

    @patch('list2term.Lines._validate_data')
    @patch('list2term.Lines._print_lines')
    @patch('list2term.Lines._clear_line')
    def test__del_item_Should_CallClearLineAndPrintLines_When_Called(self, clear_line_patch, print_lines_patch, *patches):
        lines = Lines(size=3)
        del lines[1]
        clear_line_patch.assert_called_once_with(2)
        print_lines_patch.assert_called_once_with(1)

    @patch('list2term.Lines._validate_data')
    @patch('list2term.Lines._print_lines')
    @patch('list2term.Lines._clear_line')
    def test__del_item_Should_RaiseNotImplementedError_When_CalledWithSlice(self, clear_line_patch, print_lines_patch, *patches):
        lines = Lines(size=3)
        with self.assertRaises(NotImplementedError):
            del lines[1:2]

    @patch('list2term.Lines._validate_data')
    @patch('list2term.Lines._print_lines')
    def test_append_Should_CallPrintLines_When_Called(self, print_lines_patch, *patches):
        lines = Lines(size=3)
        lines.append('hello world')
        print_lines_patch.assert_called_once_with()

    @patch('list2term.Lines._validate_data')
    @patch('list2term.Lines._print_lines')
    @patch('list2term.Lines._clear_line')
    def test_pop_Should_CallClearLineAndPrintLines_When_Called(self, clear_line_patch, print_lines_patch, *patches):
        lines = Lines(size=3)
        lines.pop(1)
        clear_line_patch.assert_called_once_with(2)
        print_lines_patch.assert_called_once_with(1)

    @patch('list2term.Lines._validate_data')
    def test__remove_Should_RaiseNotImplementedError_When_Called(self, *patches):
        lines = Lines(size=3)
        with self.assertRaises(NotImplementedError):
            lines.remove('hello world')

    @patch('list2term.list2term.sys.stderr.isatty', return_value=True)
    @patch('list2term.Lines._validate_data')
    @patch('list2term.Lines._clear_line')
    def test_clear_Should_CallClearLineForAllLines_When_Called(self, clear_line_patch, *patches):
        lines = Lines(size=3)
        lines.clear()
        for number in range(3):
            self.assertTrue(call(number) in clear_line_patch.mock_calls)

    @patch('list2term.Lines._validate_data')
    @patch('list2term.list2term.sys.stderr.isatty', return_value=True)
    @patch('list2term.Lines._get_move_char')
    @patch('builtins.print')
    def test__clear_line_Should_CallExpected_When_Tty(self, print_patch, get_move_char_patch, *patches):
        lines = Lines(size=3)
        lines._clear_line(1)
        get_move_char_patch.assert_called_once_with(1)
        print_patch.assert_called()

    @patch('list2term.Lines._validate_data')
    @patch('list2term.Lines._get_move_char')
    @patch('list2term.list2term.sys.stderr')
    @patch('builtins.print')
    def test__print_line_Should_CallExpected_When_Tty(self, print_patch, stderr_patch, *patches):
        stderr_patch.isatty.return_value = True
        lines = Lines(size=13)
        lines._current = 0
        lines._print_line(3)
        self.assertEqual(len(print_patch.mock_calls), 2)
        self.assertEqual(lines._current, 1)

    @patch('list2term.list2term.sys.stderr')
    @patch('builtins.print')
    def test__print_line_Should_CallExpected_When_Notty(self, print_patch, stderr_patch, *patches):
        stderr_patch.isatty.return_value = False
        lines = Lines(size=13)
        lines._current = 0
        lines._print_line(3)
        # print_patch.assert_not_called()
        self.assertEqual(lines._current, 0)

    @patch('list2term.Lines._get_move_char')
    @patch('list2term.list2term.sys.stderr')
    @patch('builtins.print')
    def test__print_line_Should_CallExpected_When_NoTtyButForce(self, print_patch, stderr_patch, *patches):
        stderr_patch.isatty.return_value = False
        lines = Lines(size=13)
        lines._current = 0
        lines._print_line(3, force=True)
        self.assertEqual(len(print_patch.mock_calls), 3)
        self.assertEqual(lines._current, 1)

    @patch('list2term.Lines._validate_data')
    @patch('list2term.list2term.sys.stderr')
    @patch('builtins.print')
    def test__print_x_axis_Should_CallExpected_When_TtyAndShowXaxis(self, print_patch, stderr_patch, *patches):
        stderr_patch.isatty.return_value = True
        lines = Lines(size=13, show_x_axis=True)
        lines._current = 0
        lines._print_x_axis(force=True)
        self.assertEqual(len(print_patch.mock_calls), 1)

    @patch('list2term.list2term.sys.stderr.isatty', return_value=True)
    @patch('list2term.Lines._validate_data')
    @patch('list2term.Lines._print_line')
    def test__print_lines_Should_CallExpected_When_Called(self, print_line_patch, *patches):
        lines = Lines(size=3)
        lines._print_lines()
        self.assertEqual(len(print_line_patch.mock_calls), 3)

    @patch('list2term.list2term.sys.stderr.isatty', return_value=True)
    @patch('list2term.list2term.os.get_terminal_size')
    def test__init_Should_RaiseValueError_When_TtyTerminalLinesLessThanDataSize(self, get_terminal_size_patch, *patches):
        get_terminal_size_patch.return_value = Mock(lines=2)
        with self.assertRaises(ValueError):
            Lines(size=3)

    def test__init_Should_RaiseValueError_When_LookupItemsAreNotUnique(self, *patches):
        with self.assertRaises(ValueError):
            Lines(size=3, lookup=['a', 'a', 'a'])

    def test__init_Should_RaiseValueError_When_LookupLengthIsNotSameAsSize(self, *patches):
        with self.assertRaises(ValueError):
            Lines(size=2, lookup=['a', 'b', 'c'])

    def test__init_Should_RaiseValueError_When_LookupLengthIsNotSameAsDataSize(self, *patches):
        with self.assertRaises(ValueError):
            Lines(data=['', ''], lookup=['a', 'b', 'c'])

    def test__init_Should_RaiseValueError_When_NoDataSizeLookupAttributes(self, *patches):
        with self.assertRaises(ValueError):
            Lines()

    def test__init_Should_SetDataSize_When_LookupNoDataNoSize(self, *patches):
        lookup = ['a', 'b', 'c']
        lines = Lines(lookup=lookup)
        self.assertEqual(len(lines.data), len(lookup))

    def test__init_Should_RaiseValueError_When_NoDataOrSizeAttributesProvided(self, *patches):
        with self.assertRaises(ValueError):
            Lines()

    @patch('list2term.Lines._validate_data')
    def test__sanitize_Should_ReturnExpected_When_StrLessThanMaxChars(self, *patches):
        lines = Lines(size=3)
        text = 'hello world'
        result = lines._sanitize(text)
        self.assertEqual(result, text)

    @patch('list2term.Lines._validate_data')
    def test__sanitize_Should_ReturnExpected_When_StrGreaterThanMaxChars(self, *patches):
        lines = Lines(size=3)
        text = 'hello' * 40
        result = lines._sanitize(text)
        expected_result = f'{text[0:MAX_CHARS - 3]}...'
        self.assertEqual(result, expected_result)

    @patch('list2term.Lines._validate_data')
    def test__sanitize_Should_ReturnExpected_When_NoData(self, *patches):
        lines = Lines(size=3)
        text = ''
        result = lines._sanitize(text)
        self.assertEqual(result, text)

    @patch('list2term.Lines._validate_data')
    def test__sanitize_Should_ReturnExpected_When_List(self, *patches):
        lines = Lines(size=3)
        text = ['', 'i', ' ', 'a', 'm']
        result = lines._sanitize(text)
        self.assertEqual(result, 'i am')
        lines.write('i am')

    @patch('list2term.Lines._validate_data')
    @patch('list2term.Lines._get_index_message')
    def test__write_Should_UpdateList_When_MessageMatches(self, get_index_message_patch, *patches):
        get_index_message_patch.return_value = 13, 'dios bendiga los gusanos'
        lines = Lines(size=20)
        lines.write('fobia -> dios bendiga los gusanos')
        self.assertEqual(lines[13], 'dios bendiga los gusanos')
        lines.write('fobia -> dios bendiga los gusanos')

        get_index_message_patch.return_value = None, '--original-message'
        lines.write('miel de escorpion')
        self.assertEqual(lines[13], 'dios bendiga los gusanos')

    @patch('list2term.Lines._validate_data')
    def test_get_index_message_Should_ReturnExtractedIndexAndMessage_When_LookupTable(self, *patches):
        lines = Lines(size=3, lookup=['fobia', 'mana', 'moenia'])
        index, message = lines._get_index_message('mana -> en el muelle de san blas')
        self.assertEqual(index, 1)
        self.assertEqual(message, 'en el muelle de san blas')

        index, message = lines._get_index_message('julieta venegas ->  el presente (unplugged)  ')
        self.assertIsNone(index)
        self.assertEqual(message, 'julieta venegas ->  el presente (unplugged)  ')

    @patch('list2term.Lines._validate_data')
    def test_get_index_message_Should_ReturnExtractedIndexAndMessage_When_NoLookupTable(self, *patches):
        lines = Lines(size=3)
        index, message = lines._get_index_message('mana -> en el muelle de san blas')
        self.assertIsNone(index)
        self.assertEqual(message, 'mana -> en el muelle de san blas')
