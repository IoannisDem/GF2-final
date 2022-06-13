"""Test the scanner module."""
import pytest

from scanner import Symbol, Scanner
from names import Names

test_path = "test.vi"  # test.vi is an empty test file


@pytest.fixture
def new_scanner(request):
    """Returns a new instance of the Scanner class."""
    with open(test_path, 'w') as f:
        f.write(request.param)

    new_names = Names()
    scan = Scanner(test_path, new_names)

    with open(test_path, 'w') as f:
        f.write("")
    return scan


@pytest.fixture
def new_file_handler(request):
    """Returns a new instance of the FileHandler class."""
    with open(test_path, 'w') as f:
        f.write(request.param)

    file_h = Scanner.FileHandler(test_path)

    with open(test_path, 'w') as f:
        f.write("")
    return file_h


@pytest.fixture
def new_symbol():
    """Returns a new instance of the Symbol class."""
    return Symbol()


def test_get_dict(new_symbol):
    """Tests proper return value from Symbol.get_dict()."""
    new_symbol.type = 3
    new_symbol.id = 2
    assert new_symbol.get_dict() == {'type': 3, 'id': 2}


@pytest.mark.parametrize('new_scanner',
                         ["#TEST\nAND and1(IN=4);#;->\n,->2a.[OUT]TO"],
                         indirect=True)
def test_get_symbol(new_scanner):
    """Tests get_symbol returns correct symbols"""

    # Perform scanner tests
    assert new_scanner.get_symbol().type == new_scanner.KEYWORD  # TYPE KEYWORD
    assert new_scanner.get_symbol().type == new_scanner.NAME  # TYPE NAME
    assert new_scanner.get_symbol().type == new_scanner.OPEN_PARENTHESIS
    assert new_scanner.get_symbol().type == new_scanner.IN
    assert new_scanner.get_symbol().type == new_scanner.EQUALS
    assert new_scanner.get_symbol().type == new_scanner.NUMBER
    assert new_scanner.get_symbol().type == new_scanner.CLOSE_PARENTHESIS
    assert new_scanner.get_symbol().type == new_scanner.SEMICOLON
    assert new_scanner.get_symbol().type == new_scanner.COMMA
    assert new_scanner.get_symbol().type == new_scanner.CONNECTION
    assert new_scanner.get_symbol().type == new_scanner.NUMBER
    assert new_scanner.get_symbol().type == new_scanner.NAME
    assert new_scanner.get_symbol().type == new_scanner.FULLSTOP
    assert new_scanner.get_symbol().type == new_scanner.OPEN_SQUARE_BRACKET
    assert new_scanner.get_symbol().type == new_scanner.OUT
    assert new_scanner.get_symbol().type == new_scanner.CLOSE_SQUARE_BRACKET
    assert new_scanner.get_symbol().type == new_scanner.TO
    assert new_scanner.get_symbol().type == new_scanner.EOF


@pytest.mark.parametrize('new_scanner',
                         ["#TEST\nAND and1(IN=4);#;->\n,->2a.[OUT]TO"],
                         indirect=True)
def test_get_line_details(new_scanner):
    """Tests get_line_details returns correct info"""
    assert new_scanner.get_line_details() == (1, "#TEST\n", -1)
    _ = new_scanner.get_symbol()
    assert new_scanner.get_line_details() == (2, "AND and1(IN=4);#;->\n", 2)


@pytest.mark.parametrize('new_file_handler, text',
                         [("#TEST\nAND and1(IN=4);#;->\n,->2a.[OUT]TO",
                          "#TEST\nAND and1(IN=4);#;->\n,->2a.[OUT]TO")],
                         indirect=['new_file_handler'])
def test_advance(new_file_handler, text):
    """Tests advance returns next character"""
    for i in range(len(text)-1):
        assert new_file_handler.advance() == text[i+1]
    assert new_file_handler.advance() == ""
    assert new_file_handler.advance() == ""


@pytest.mark.parametrize('new_file_handler',
                         ['     nand'], indirect=True)
def test__skip_spaces(new_file_handler):
    """Tests _skip_spaces appropriately handles spaces"""
    assert new_file_handler._skip_spaces() == 'n'


@pytest.mark.parametrize('new_file_handler',
                         ['a#sw2 -> and1\nb'],
                         indirect=True)
def test__skip_comments(new_file_handler):
    """Tests _skip_comments skips to next line"""
    assert new_file_handler._skip_comments() == 'a'
    _ = new_file_handler.advance()
    assert new_file_handler._skip_comments() == 'b'


@pytest.mark.parametrize('new_file_handler',
                         ['a -> b#connection\nc'],
                         indirect=True)
def test_skip_formatting(new_file_handler):
    """Tests _skip_formatting skips both comments and spaces"""
    assert new_file_handler.skip_formatting() == 'a'
    _ = new_file_handler.advance()
    assert new_file_handler.skip_formatting() == '-'
    _ = new_file_handler.advance()
    _ = new_file_handler.advance()
    assert new_file_handler.skip_formatting() == 'b'
    _ = new_file_handler.advance()
    assert new_file_handler.skip_formatting() == 'c'


@pytest.mark.parametrize('new_file_handler',
                         ['a234 b'],
                         indirect=True)
def test_get_number_exceptions(new_file_handler):
    """Tests get_number handles exceptions"""
    with pytest.raises(ValueError):
        new_file_handler.get_number()


@pytest.mark.parametrize('new_file_handler',
                         ['234 3'],
                         indirect=True)
def test_get_number(new_file_handler):
    """Tests get_number obtains full appropriate number"""
    assert new_file_handler.get_number() == 234


@pytest.mark.parametrize('new_file_handler',
                         ['_AB', '3aR'],
                         indirect=True)
def test_get_name_exceptions(new_file_handler):
    """Tests get_name handles exceptions"""
    with pytest.raises(ValueError):
        new_file_handler.get_name()


@pytest.mark.parametrize('new_file_handler',
                         ['A2b c'],
                         indirect=True)
def test_get_name(new_file_handler):
    """Tests get_name obtains full appropriate name"""
    assert new_file_handler.get_name() == 'A2b'


@pytest.mark.parametrize('new_file_handler',
                         [' 3ab4_] ;2'],
                         indirect=True)
def test_get_str(new_file_handler):
    """Tests get_str obtains string without spaces"""
    assert new_file_handler.get_str() == '3ab4_]'


@pytest.mark.parametrize('new_file_handler',
                         [' 34ab#a->;\n\n A3'],
                         indirect=True)
def test__get_next_line(new_file_handler):
    """Tests get_str obtains string without spaces"""
    assert new_file_handler._get_next_line() == 'A'

    # End of file, no more lines
    assert new_file_handler._get_next_line() is None
