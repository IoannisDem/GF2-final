"""Tracks and displays errors.

Used in the Logic Simulator project to track and display the syntactic and
semantic errors generated when parsing and building the logic network.

Classes
-------
ErrorHandler - Tracks and displays errors.
"""


class ErrorHandler:
    """Tracks and displays errors.

    An instance of this class is passed to every class where a potential error
    may arise. This class keeps track of the error IDs, error messages, and
    gives the user a way to display the errors.

    Classes
    -------
    Error: Tracks information about a single error.

    Syntax: Contains details of all syntax errors.

    Semantic: Contains details of all semantic errors.

    Public methods
    --------------
    add_error(self, error_id, line_number, line, current_index): Records an
            error and the details about its type and location.

    display_errors(self): Displays the recorded errors.

    get_error_message(self, error_id): Returns the message associated with
            the error_id.

    error_builder(self, error): Pretty prints the error.

    syntactic_marker(self, error_id, line): Returns the location error.

    get_error_type(self, error_id): Returns whether the error is syntactic
            or semantic.
    """

    def __init__(self, names):
        """ Initialises classes and variables. """

        self.syntax = self.Syntax(names)
        self.semantic = self.Semantic(names)

        self.error_list = []
        self.error_count = 0
        self.syntax_error_count = 0

        self.loc_err = False    

    def add_error(self, error_id, line_number, line, current_index, opt_cur_index=None, override=False):
        """ Records an error and the details about its type and location. """
        if not override and error_id in self.semantic.syn_li:
            current_index = self.syntactic_marker(line,opt_cur_index)
        self.error_list.append(self.Error(
            error_id, line_number, line, current_index))
        self.error_count += 1
        
        if self.syntax.is_error_syntactic(error_id):
            self.syntax_error_count += 1

    def display_errors(self):
        """ Displays the recorded errors. """
        print(self.error_count, 'errors detected:')
        for error in self.error_list:
            print('ERROR:', self.error_builder(error))

    # ----------------------------------------------------------------------- #

    def get_error_message(self, error_id):
        """ Returns the message associated with the error_id. """
        if self.syntax.is_error_syntactic(error_id):
            return self.syntax.error_message[error_id]
        elif self.semantic.is_error_semantic(error_id):
            return self.semantic.error_message[error_id]
        else:
            raise Exception('Unknown error')

    def error_builder(self, error):
        """ Pretty prints the error. """
        # makes printable error message for output

        error_type = self.get_error_type(error.error_id)
        error_msg = self.get_error_message(error.error_id)

        if error.current_index is None:

            message = [
                error_type, 'Error on line ', str(error.line_number), ':\n',
                error.line,
                error_msg, '\n'
            ]
        else:
            error_pointer = ' '*error.current_index + '^'

            message = [
                error_type, 'Error on line ', str(error.line_number), ':\n',
                error.line,
                error_pointer, '\n',
                error_msg, '\n'
            ]

        return ''.join(message)

    def syntactic_marker(self, line,opt_cur_index):
        """ Returns the location error. """
        count = 0
        marker = 0
        for i in range(len(line)):
            if count == 0 and line[i].isspace():
                count = 0
                marker +=1
            elif count == opt_cur_index:
                count = count
            elif line[i] and line[i-1].isspace():
                count += 1
                marker += 1
            elif line[i] and not line[i].isspace():
                marker += 1
        marker -= 2
        return marker
    

    def get_error_type(self, error_id):
        """ Returns whether the error is syntactic or semantic. """
        if self.syntax.is_error_syntactic(error_id):
            return 'Syntax'
        elif self.semantic.is_error_semantic(error_id):
            return 'Semantic'
        else:
            raise Exception('Unknown error')

    # ----------------------------------------------------------------------- #

    class Error:
        """ Tracks information about a single error. """

        def __init__(self, error_id, line_number, line, current_index):
            self.error_id = error_id
            self.line_number = line_number
            self.line = line
            self.current_index = current_index

    class Syntax:
        """ Contains details of all syntax errors. """

        def __init__(self, names):
            """ Initialise error ids and messages. """
            self.names = names

            [self.MISSING_SEMICOLON, self.MISSING_EQUALS, self.MISSING_PORT,
             self.MISSING_OPEN_PARENTHESIS, self.MISSING_CLOSE_PARENTHESIS,
             self.MISSING_CLOSE_SQUARE_BRACKET, self.MISSING_TO,
             self.MISSING_IN, self.MISSING_CONNECTION, self.MISSING_PERIOD,

             self.NOT_NAME, self.NOT_NUMBER, self.NOT_BINARY_DIGIT,
             self.RESERVED_NAME,

             self.MISSING_KEYWORD,
             
             self.MISSING_OUT, self.MISSING_COMMA,
             
             self.MISSING_OPEN_CURLY_BRACKET,
             self.MISSING_CLOSE_CURLY_BRACKET,
             
             self.INVALID_CIRCUIT_KEYWORD,
             
             self.EMPTY_FILE,
             ] = self.names.unique_error_codes(21)

            self.error_message = {
                self.MISSING_SEMICOLON: 'Missing comma or semicolon',
                self.MISSING_EQUALS: 'Missing equals',
                self.MISSING_PORT: 'Missing port',
                self.MISSING_OPEN_PARENTHESIS: 'Missing open parenthesis',
                self.MISSING_CLOSE_PARENTHESIS: 'Missing close parenthesis',
                self.MISSING_CLOSE_SQUARE_BRACKET:
                    'Missing close square bracket',
                self.MISSING_TO: 'Missing TO',
                self.MISSING_IN: 'Missing IN',
                self.MISSING_CONNECTION: 'Missing -> connection',
                self.MISSING_PERIOD: 'Missing clock PERIOD',
                self.NOT_NAME:
                    'Expected a name, must be alphanumeric '
                    'and begin with an alphabet.',
                self.NOT_NUMBER: 'Expected a number',
                self.NOT_BINARY_DIGIT: 'Expected a binary digit 0 or 1',
                self.RESERVED_NAME:
                    'This cannot be used as a name since '
                    'it is a keyword.',
                self.MISSING_KEYWORD:
                    'Expected a keyword such as NAND, '
                    'MONITOR etc',
                self.MISSING_OUT: 'Missing OUT',
                self.MISSING_COMMA: 'Missing "," COMMA',
                
                self.MISSING_OPEN_CURLY_BRACKET: 'Missing open curly bracket',
                self.MISSING_CLOSE_CURLY_BRACKET:
                    'Missing close curly bracket',
                
                self.INVALID_CIRCUIT_KEYWORD:
                    'Can only create gates and connections in a circuit ',
                
                self.EMPTY_FILE: 'The definition file must not be empty',
            }

        def is_error_syntactic(self, error_id):
            """ Checks if error is syntactic. """
            if error_id in self.error_message:
                return True
            else:
                return False

    class Semantic:
        """ Contains details of all semantic errors. """

        def __init__(self, names):
            """ Initialise error ids and messages. """

            self.names = names

            self.syn_li = [
                self.INVALID_PINS,
                self.LOOP_INDEX_BAD_ORDER,
            ] = list(self.names.unique_error_codes(2))

            self.error_message = {
                self.INVALID_PINS: 'Device must have inputs between 1 and 16',
                self.LOOP_INDEX_BAD_ORDER: 'Need loop index1 <= index2',
            }

        def create_syn_list(self, net_li):
            """ Extend syn_li list with errors. """
            new_li = [self.NO_ERROR, self.INPUT_TO_INPUT,
                      self.OUTPUT_TO_OUTPUT,
                      self.INPUT_CONNECTED, self.PORT_ABSENT,
                      self.DEVICE_ABSENT,
                      self.NOT_INPUT, self.NOT_OUTPUT] = net_li
            self.syn_li.extend(new_li)

        def define_error_messages(self, error_message_dict):
            """ Updates the error messages. """
            self.error_message.update(error_message_dict)

        def is_error_semantic(self, error_id):
            """ Checks if the error is semantic. """
            if error_id in self.error_message:
                return True
            else:
                return False
