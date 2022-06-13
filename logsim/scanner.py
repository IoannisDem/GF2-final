"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""
from os.path import exists


class Symbol:
    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    No parameters.

    Public methods
    --------------
    No public methods.
    """

    def __init__(self):
        """Initialise symbol properties."""
        self.type = None
        self.id = None

        self.val = None

        self.current_index = None
        self.line_number = None     

    def get_dict(self):
        """TODO: remove this?"""
        return {'type': self.type, 'id': self.id}


class Scanner:
    """Read circuit definition file and translate the characters into symbols.

    Once supplied with the path to a valid definition file, the scanner
    translates the sequence of characters in the definition file into symbols
    that the parser can use. It also skips over comments and irrelevant
    formatting characters, such as spaces and line breaks.

    Parameters
    ----------
    path: path to the circuit definition file.
    names: instance of the names.Names() class.

    Public methods
    -------------
    get_symbol(self): Translates the next sequence of characters into a symbol
                      and returns the symbol.
    get_line_details(self, line_number=None): Get line number, line and
        position of the current character.

    Sub-Classes
    -----------
    FileHandler: Reads the definition file and extracts names and numbers.
    """

    def __init__(self, path, names):
        """Open specified file and initialise reserved words and IDs."""

        self.names = names

        self.symbol_type_list = [
            self.KEYWORD, self.NUMBER, self.NAME,
            self.COMMA, self.SEMICOLON, self.EQUALS, self.CONNECTION,
            self.EOF, self.FULLSTOP,
            self.OPEN_PARENTHESIS, self.CLOSE_PARENTHESIS,
            self.OPEN_SQUARE_BRACKET, self.CLOSE_SQUARE_BRACKET,
            self.TO, self.IN, self.OUT, self.PERIOD,
            self.OPEN_CURLY_BRACKET, self.CLOSE_CURLY_BRACKET,
        ] = range(19)

        self.unichar_punctuation = {
            ',': self.COMMA, ';': self.SEMICOLON, '=': self.EQUALS,
            '': self.EOF, '.': self.FULLSTOP,
            '(': self.OPEN_PARENTHESIS, ')': self.CLOSE_PARENTHESIS,
            '[': self.OPEN_SQUARE_BRACKET, ']': self.CLOSE_SQUARE_BRACKET,
            '{': self.OPEN_CURLY_BRACKET, '}': self.CLOSE_CURLY_BRACKET,
        }



        self.alpha_punctuation = {'TO': self.TO, 'IN': self.IN,
                                  'OUT': self.OUT, 'PERIOD': self.PERIOD}

        self.keywords_list = ['AND', 'OR', 'NAND', 'NOR', 'XOR', 'DTYPE',
                              'CONNECT', 'CIRCUIT', 'MONITOR', 'CLOCK',
                              'SWITCH', 'NOT', 'CIRCUIT', 'INPUT', 'OUTPUT']

        [self.AND_ID, self.OR_ID, self.NAND_ID, self.NOR_ID, self.XOR_ID,
         self.DTYPE_ID, self.CONNECT_ID, self.CIRCUIT_ID, self.MONITOR_ID,
         self.CLOCK_ID, self.SWITCH_ID, self.NOT_ID, self.CIRCUIT_ID,
         self.INPUT_ID, self.OUTPUT_ID,
         ] = self.names.lookup(self.keywords_list)

        self.fileHandler = Scanner.FileHandler(path)

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
        symbol = Symbol()
        self.fileHandler.skip_formatting()

        if self.fileHandler.current_character.isalpha():
            name_string = self.fileHandler.get_name()

            symbol.val = name_string

            if name_string in self.keywords_list:
                symbol.type = self.KEYWORD
                [symbol.id] = self.names.lookup([name_string])
                symbol.current_index = self.fileHandler.current_index

            elif name_string in self.alpha_punctuation:
                symbol.type = self.alpha_punctuation[name_string]
                symbol.current_index = self.fileHandler.current_index
            else:
                symbol.type = self.NAME
                [symbol.id] = self.names.lookup([name_string])
                symbol.line_number = self.fileHandler.line_number
                symbol.current_index = self.fileHandler.current_index

        elif self.fileHandler.current_character.isdigit():
            symbol.id = self.fileHandler.get_number()
            symbol.type = self.NUMBER
            symbol.current_index = self.fileHandler.current_index
            symbol.val = symbol.id  # only for debugging, remove later

        elif self.fileHandler.current_character in self.unichar_punctuation:
            symbol.type = self.unichar_punctuation[
                self.fileHandler.current_character]

            symbol.val = self.fileHandler.current_character
            symbol.current_index = self.fileHandler.current_index

            self.fileHandler.advance()
        else:
            name_str = self.fileHandler.get_2chars()

            if name_str == '->':
                symbol.type = self.CONNECTION
            else:
                symbol.type = None
            symbol.current_index = self.fileHandler.current_index
            symbol.val = self.fileHandler.current_character

        return symbol

    def get_line_details(self, line_number=None):
        """Get line number, line and position of the current character.

        Useful for printing out errors."""
        if line_number is None:
            if self.fileHandler.line_number < len(self.fileHandler.lines):
                return(self.fileHandler.line_number + 1,
                       self.fileHandler.lines[self.fileHandler.line_number],
                       self.fileHandler.current_index - 1)
            else:
                return(self.fileHandler.line_number,
                       self.fileHandler.lines[
                           self.fileHandler.line_number - 1],
                       self.fileHandler.current_index - 1)
        else:
            return line_number + 1, self.fileHandler.lines[line_number], None

    class FileHandler:
        """Reads the definition file and extracts names and numbers.

        This class contains many helper functions to read and extract data from
        the definition file. It skips over irrelevant formatting characters,
        such as spaces and line breaks.

        Parameters
        ----------
        path - path to the definition file.
        skip_spaces(self): Skips spaces such that current character is not
                           a space

        Public methods
        --------------
        advance(self): Reads and returns the next character in the file.

        skip_formatting(self): Skips all comments and whitespaces and return
                               the next character.

        get_number(self): Returns the number beginning at the current pointer
                          location.

        get_name(self): Returns the name beginning at current pointer location
                        in file.

        get_2chars(self): Return the next 2 character.

        close(self): Closes the file.

        Private methods
        --------------
        _skip_spaces(self): Skips spaces and returns the next character.

        _skip_comments(self): Skips all comments and returns the next
                              character.

        _get_next_line(self): Skips the pointer to the next line and returns
                              the first character.
        """

        def __init__(self, path):
            """Open the file specified by the path."""
            if exists("definition_files/" + path):
                path = "definition_files/" + path
            
            self.file = open(path, 'r')

            self.lines = self.file.readlines()
            if len(self.lines) > 0:
                self.lines[-1] += '\n'
            self.lines.append(' \n')

            self.line_number = 0
            self.current_index = -1

            self.current_character = None
            self.advance()

        def advance(self):
            """ Reads and returns the next character in the file."""

            if self.line_number >= len(self.lines):
                return ''

            self.current_index += 1

            if self.current_index >= len(self.lines[self.line_number]):
                self.line_number += 1


                self.current_index = 0

            if self.line_number >= len(self.lines):
                self.current_character = ''
            else:
                self.current_character = \
                    self.lines[self.line_number][self.current_index]

            return self.current_character

        def _skip_spaces(self):
            """ Skips spaces and returns the next character."""
            c = self.current_character

            while c.isspace():
                c = self.advance()

            self.current_character = c

            return c

        def _skip_comments(self):
            """ Skips all comments and returns the next character."""
            c = self.current_character

            while c == '#':
                c = self._get_next_line()

            self.current_character = c

            return c

        def skip_formatting(self):
            """ Skips all comments and whitespaces and return the next
            character."""
            c = self.current_character

            while c.isspace() or c == '#':
                self._skip_spaces()
                c = self._skip_comments()

            self.current_character = c

            return c

        def get_number(self):
            """ Returns the number beginning at the current pointer location.
            """
            c = self.current_character

            if not c.isdigit():
                raise ValueError('Current character expected to be a number.')

            str_number = c

            c = self.advance()
            while c.isdigit():
                str_number += c
                c = self.advance()

            self.current_character = c

            return int(str_number)

        def get_name(self):
            """ Returns the name beginning at current pointer location in file.
            """

            c = self.current_character

            if not c.isalpha():
                raise ValueError('Current character expected '
                                 'to be a alphabet.')

            name = c        

            c = self.advance()

            while c.isalnum():
                name += c
                c = self.advance()

            self.current_character = c

            return name

        def get_2chars(self):
            """ Return the next 2 character."""
            c = self.current_character

            str_name = c

            c = self.advance()
            str_name += c

            c = self.advance()
            self.current_character = c

            return str_name

        def _get_next_line(self):
            """ Skips the pointer to the next line and returns the first
            character."""
            c = self.current_character
            while c != '\n' and c != '\r' and c != '':
                c = self.advance()

            c = self._skip_spaces()

            if c == '':
                c = None

            return c

        def close(self):
            """Closes the file."""
            self.file.close()
