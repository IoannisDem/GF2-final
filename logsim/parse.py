"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""

'''
TODOs
-----
Multiple stopping symbols (keywords are stopping symbols)
Define a local error stack?
You worry about ";" not being added at the end of the line, but
you will also face issues when ";" appears too early. In this case,
you must immediately skip symbols to next line, you cannot move on to the
next symbol before doing the skipping.
If you import a file, you need extra error messages when there is a
name clash with something from the import file. Add import
functionality in the end
Sometimes a fullstop '.' might be necessary since it is essential to describe a
port. You must ensure that you raise an error. Right now a port is considered
optional. Error is either semantic or syntactic.
if you don't input a valid command, it is skipped!!!!


NOTEs
-----
You should keep parsing even if you encounter errors but you should
stop building the network


KNOWN BUGs
----------
If you end the code with an error, like if this is the last line of code:
SWITCHSET a = -1;
then you run into an infinite loop!!
'''


class Parser:
    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.
    errorHandler: instance of ErrorHandler class for reporting errors.

    Public methods
    --------------
    parse_network(self): Parses the circuit definition file.

    Private methods
    ---------------
    _circuit(self): Parses and executes a circuit command

    _not_list(self, circ_name=None): Parses and executes a NOT command

    _switch(self): Parses and executes a switch command

    _connectlist(self, circ_name=None): Parses and executes a connect command

    _xor_list(self, circ_name=None): Parses and executes a XOR command

    _monitor_list(self): Parses and execute a monitors command

    _clock(self): Parses and execute a clocks command

    _gate_list(self, circ_name=None): Parses and executes a
        gate command (AND, NAND, OR, NOR)

    _dtype(self, circ_name=None): Parses and executes a dtype command

    _skip_to_stopping_symbol(self): Skips to the next stopping symbol

    _name(self): Checks if current symbol is a name and returns it

    _port(self): Returns the port

    _signame(self): Returns the signame (signal and port)

    _number(self): Checks if current symbol is a number and returns it

    _pin_input(self): Parses the number of inputs

    _input_period(self): Parses the number of period

    _binary_digit(self): Checks if the current symbol is a binary digit and
        returns it

    _loop_times(self): Parses the name loop and returns the indices

    _is_it_name(self, name_id): Checks if name_id corresponds to a valid name

    _is_equals(self): Checks if the current symbol is an equals

    _is_comma(self): Checks if the current symbol is a comma

    _is_semicolon(self): Checks if the current symbol is an semicolon

    _is_close_square_bracket(self): Checks if the current symbol
        is a ']' closed square bracket

    _is_to(self): Checks if the current symbol is a TO

    _is_connection(self): Checks if the current symbol is a '->' connection

    _is_open_parenthesis(self): Checks if the current symbol is a '(' open
        parenthesis

    _is_close_parenthesis(self): Checks if the current symbol is a ')' close
        parenthesis

    _is_open_curly_bracket(self): Checks if the current symbol is a '{'
        open curly brace

    _is_close_curly_bracket(self): Checks if the current symbol
        is a '}' close curly brace

    _is_in(self): Checks if the current symbol is a IN

    _is_period(self): Checks if the current symbol is a PERIOD
    """

    def __init__(self, names, devices, network, monitors, scanner,
                 errorHandler):
        """Initialise constants."""
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner
        self.errorHandler = errorHandler

        self.stopping_symbols = [self.scanner.SEMICOLON, self.scanner.COMMA,
                                 self.scanner.KEYWORD, self.scanner.EOF,
                                 self.scanner.CLOSE_CURLY_BRACKET]

        self.symbol = None

    def parse_network(self):
        """Parses the circuits definition file."""

        self.symbol = self.scanner.get_symbol()

        if self.symbol.type == self.scanner.EOF:
            self.errorHandler.add_error(
                self.errorHandler.syntax.EMPTY_FILE,
                *self.scanner.get_line_details()
            )

        while self.symbol.type != self.scanner.EOF:
            if self.symbol.type == self.scanner.KEYWORD:
                if self.symbol.id == self.scanner.SWITCH_ID:
                    self._switch()
                elif self.symbol.id == self.scanner.CONNECT_ID:
                    self._connectlist()
                elif self.symbol.id == self.scanner.XOR_ID:
                    self._xor_list()
                elif self.symbol.id == self.scanner.MONITOR_ID:
                    self._monitor_list()
                elif self.symbol.id == self.scanner.CLOCK_ID:
                    self._clock()
                elif self.symbol.id in [self.scanner.AND_ID,
                                        self.scanner.OR_ID,
                                        self.scanner.NAND_ID,
                                        self.scanner.NOR_ID]:
                    self._gate_list()
                elif self.symbol.id == self.scanner.DTYPE_ID:
                    self._dtype()
                elif self.symbol.id == self.scanner.NOT_ID:
                    self._not_list()
                elif self.symbol.id == self.scanner.CIRCUIT_ID:
                    self._circuit()
                else:
                    self.errorHandler.loc_err = True
                    self.errorHandler.add_error(
                        self.errorHandler.syntax.MISSING_KEYWORD,
                        *self.scanner.get_line_details()
                    )

                    self.symbol = self._skip_to_stopping_symbol()
                    self.errorHandler.loc_err = False
            else:
                if self.symbol.type == self.scanner.SEMICOLON:
                    self.errorHandler.loc_err = False
                    self.symbol = self.scanner.get_symbol()
                elif self.symbol.type == self.scanner.COMMA:
                    self.errorHandler.loc_err = False
                    self.symbol = self.scanner.get_symbol()
                else:
                    self.errorHandler.loc_err = True
                    self.errorHandler.add_error(
                        self.errorHandler.syntax.MISSING_KEYWORD,
                        *self.scanner.get_line_details()
                    )

                    self.symbol = self._skip_to_stopping_symbol()
                    self.errorHandler.loc_err = False
                    # print(self.symbol.val)
        self.errorHandler.display_errors()

        return True

    def _circuit(self):
        """Parses and executes a circuit command"""

        class CircuitConnectionHolder:
            """Holds on to the details of a single circuit connection"""

            def __init__(self, circ_name, circuit_port_id, device_name_id,
                         device_port_id, line_number):
                self.circ_name = circ_name
                self.circuit_port_id = circuit_port_id
                self.device_name_id = device_name_id
                self.device_port_id = device_port_id
                self.line_number = line_number

        def _single_connect(circ_name):
            """Parses and extracts details of a single connection within
            the circuit"""
            circuit_port_id = self._port()
            self._is_equals()
            device_name_id, device_port_id, line_number = self._signame()

            device_name = self.names.get_name_string(device_name_id)
            circ = self.names.get_name_string(circ_name)
            device_name = circ + '_' + device_name
            [device_name_id] = self.names.lookup([device_name])

            return circuit_port_id, device_name_id, device_port_id, line_number

        def _connect_inputs(circ_name):
            """Extracts and stores circuit inputs"""
            print(circ_name)
            if(self.symbol.type == self.scanner.KEYWORD and
               self.symbol.id == self.scanner.INPUT_ID):
                print('connect inputs')

                self.symbol = self.scanner.get_symbol()

                connection_holder_list = []

                print(11111)

                circuit_port_id, device_name_id, \
                    device_port_id, line_number = _single_connect(
                        circ_name)
                connection_holder_list.append(CircuitConnectionHolder(
                    circ_name,
                    circuit_port_id, device_name_id, device_port_id,
                    line_number
                ))

                print(22222)

                self.errorHandler.loc_err = False
                while self.symbol.type == self.scanner.COMMA:
                    self.symbol = self.scanner.get_symbol()
                    print(44444, self.symbol.val)

                    circuit_port_id, device_name_id, \
                        device_port_id, line_number = _single_connect(
                            circ_name)
                    connection_holder_list.append(CircuitConnectionHolder(
                        circ_name,
                        circuit_port_id, device_name_id, device_port_id,
                        line_number
                    ))

                    print(55555)

                    self.errorHandler.loc_err = False

                print(88888, self.symbol.val)
                self._is_semicolon()
                print(1919191919, self.symbol.val)
                self.errorHandler.loc_err = False

                print(77777, self.errorHandler.syntax_error_count)

                if self.errorHandler.syntax_error_count == 0:
                    for connection_holder in connection_holder_list:
                        error_type = self.network.add_circuit_input(
                            connection_holder.circ_name,
                            connection_holder.circuit_port_id,
                            connection_holder.device_name_id,
                            connection_holder.device_port_id
                        )

                        print('error ip', error_type - self.network.NO_ERROR)

                        if error_type != self.network.NO_ERROR:
                            self.errorHandler.add_error(
                                error_type,
                                *self.scanner.get_line_details(
                                    connection_holder.line_number),
                                override=True)

                self.errorHandler.loc_err = False
            else:
                raise Exception('Non-user exception')

        def _connect_outputs(circ_name):
            """Extracts and stores circuit outputs"""
            if(self.symbol.type == self.scanner.KEYWORD and
               self.symbol.id == self.scanner.OUTPUT_ID):
                print('connect outputs')

                self.symbol = self.scanner.get_symbol()

                connection_holder_list = []

                circuit_port_id, device_name_id, \
                    device_port_id, line_number = _single_connect(
                        circ_name)
                connection_holder_list.append(CircuitConnectionHolder(
                    circ_name, circuit_port_id, device_name_id, device_port_id,
                    line_number
                ))

                self.errorHandler.loc_err = False
                while self.symbol.type == self.scanner.COMMA:
                    self.symbol = self.scanner.get_symbol()

                    circuit_port_id, device_name_id, \
                        device_port_id, line_number = _single_connect(
                            circ_name)
                    connection_holder_list.append(CircuitConnectionHolder(
                        circ_name, circuit_port_id,
                        device_name_id, device_port_id,
                        line_number
                    ))

                    self.errorHandler.loc_err = False

                self._is_semicolon()
                self.errorHandler.loc_err = False

                if self.errorHandler.syntax_error_count == 0:
                    for connection_holder in connection_holder_list:
                        error_type = self.network.add_circuit_output(
                            connection_holder.circ_name,
                            connection_holder.circuit_port_id,
                            connection_holder.device_name_id,
                            connection_holder.device_port_id)

                        if error_type != self.network.NO_ERROR:
                            self.errorHandler.add_error(
                                error_type,
                                *self.scanner.get_line_details(
                                    connection_holder.line_number),
                                override=True)

                self.errorHandler.loc_err = False
            else:
                raise Exception('Non-user exception')

        def _command(circ_name):
            """Executes a single command within the circuit"""
            if self.symbol.type == self.scanner.KEYWORD:
                if self.symbol.id == self.scanner.CONNECT_ID:
                    self._connectlist(circ_name=circ_name)
                elif self.symbol.id == self.scanner.XOR_ID:
                    self._xor_list(circ_name)
                elif self.symbol.id in [self.scanner.AND_ID,
                                        self.scanner.OR_ID,
                                        self.scanner.NAND_ID,
                                        self.scanner.NOR_ID]:
                    self._gate_list(circ_name)
                elif self.symbol.id == self.scanner.DTYPE_ID:
                    self._dtype(circ_name)
                elif self.symbol.id == self.scanner.NOT_ID:
                    self._not_list(circ_name)
                elif self.symbol.id == self.scanner.INPUT_ID:
                    _connect_inputs(circ_name)
                    print(1010101010)
                elif self.symbol.id == self.scanner.OUTPUT_ID:
                    _connect_outputs(circ_name)
                else:
                    self.errorHandler.loc_err = True
                    self.errorHandler.add_error(
                        self.errorHandler.syntax.INVALID_CIRCUIT_KEYWORD,
                        *self.scanner.get_line_details()
                    )

                    self.symbol = self._skip_to_stopping_symbol()
                    self.errorHandler.loc_err = False
                    return False
            elif self.symbol.type == self.scanner.SEMICOLON:
                self.errorHandler.loc_err = False
                self.symbol = self.scanner.get_symbol()
            elif self.symbol.type == self.scanner.COMMA:
                self.errorHandler.loc_err = False
                self.symbol = self.scanner.get_symbol()
            else:
                self.errorHandler.loc_err = True
                self.errorHandler.add_error(
                    self.errorHandler.syntax.INVALID_CIRCUIT_KEYWORD,
                    *self.scanner.get_line_details()
                )

                self.symbol = self._skip_to_stopping_symbol()
                self.errorHandler.loc_err = False
                return False
            return True
            print(1111111111)

        if(self.symbol.type == self.scanner.KEYWORD and
           self.symbol.id == self.scanner.CIRCUIT_ID):
            print('CIRCUIT')

            self.symbol = self.scanner.get_symbol()

            circ_name, _ = self._name()
            # TODO: loop for every name!!!!!!
            # TODO: check if the names are distinct

            error_type = self.devices.make_circuit(circ_name)
            if error_type != self.devices.NO_ERROR:
                self.errorHandler.add_error(
                    error_type,
                    *self.scanner.get_line_details()
                )

            self._is_open_curly_bracket()
            # self.errorHandler.loc_err = False
            print(1212121212)

            command_success = _command(circ_name)

            while((self.symbol.type == self.scanner.KEYWORD or
                   self.symbol.type == self.scanner.SEMICOLON or
                   self.symbol.type == self.scanner.COMMA)
                  and command_success):
                print(self.symbol.val, 33)
                command_success = _command(circ_name)
                # self.errorHandler.loc_err = False
            print(self.symbol.val, 33)

            print(1313131313)

            self._is_close_curly_bracket()

            # self._is_semicolon()
            self.errorHandler.loc_err = False

    def _not_list(self, circ_name=None):
        """Parses and executes a NOT command"""
        class NotHolder:
            """Holds on to the details of a single NOT"""

            def __init__(self, name_id, loop=False,
                         index1=None, index2=None, line_number=None,
                         circ_name=None):
                self.name_id = name_id
                self.loop = loop

                self.line_number = line_number

                if loop:
                    self.index1 = index1
                    self.index2 = index2

                self.circ_name = circ_name

        def _get_flat_list(notHolder):
            """Converts the Holder into a list of dictionaries containing its
            attributes"""
            if notHolder.loop:
                flat_list = []
                for index in range(notHolder.index1,
                                   notHolder.index2 + 1):
                    org_name = self.names.get_name_string(
                        notHolder.name_id)
                    # creating new_names using index
                    new_name = org_name + str(index)

                    if notHolder.circ_name is not None:
                        circ = self.names.get_name_string(
                            notHolder.circ_name)
                        new_name = circ + '_' + new_name

                    # assigning IDs in new_names
                    [new_name_id] = self.names.lookup([new_name])
                    # list of dictionaries
                    flat_list.append({
                        'id': new_name_id,
                        'line_number': notHolder.line_number})
                return flat_list
            else:
                name_id = notHolder.name_id
                if notHolder.circ_name is not None:
                    name = self.names.get_name_string(
                        notHolder.name_id)
                    circ = self.names.get_name_string(
                        notHolder.circ_name)
                    name = circ + '_' + name
                    [name_id] = self.names.lookup([name])

                return [{'id': name_id,
                         'line_number': notHolder.line_number}]

        def _single_not(circ_name=None):
            """Parse and extract details of a single NOT"""
            name_id, line_number = self._name()
            # initialise variables
            loop = False
            index1 = None
            index2 = None

            # if there is '[' then it uses loop
            if self.symbol.type == self.scanner.OPEN_SQUARE_BRACKET:
                loop = True

                self.symbol = self.scanner.get_symbol()
                index1, index2 = self._loop_times()
                self._is_close_square_bracket()

            # returns an object with switch information
            return NotHolder(name_id, loop,
                             index1, index2, line_number, circ_name)

        if(self.symbol.type == self.scanner.KEYWORD and
           self.symbol.id == self.scanner.NOT_ID):
            # print('SWITCH')
            self.symbol = self.scanner.get_symbol()

            not_list = []
            # SwitchHolder object
            not_holder = _single_not(circ_name)
            if not self.errorHandler.loc_err:
                # list of dictionaries
                not_list.extend(_get_flat_list(not_holder))

            # check for local error
            self.errorHandler.loc_err = False
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()

                not_holder = _single_not(circ_name)
                if not self.errorHandler.loc_err:
                    not_list.extend(_get_flat_list(not_holder))

                self.errorHandler.loc_err = False

            self.errorHandler.loc_err = False
            self._is_semicolon()     # do something with the error

            self.errorHandler.loc_err = False

            if self.errorHandler.syntax_error_count == 0:
                for not_dict in not_list:
                    error_type = self.devices.make_device(
                        not_dict['id'],
                        self.devices.NOT)

                    print('switch:',
                          self.names.get_name_string(not_dict['id']),
                          'error:', error_type != self.devices.NO_ERROR,
                          error_type - self.devices.NO_ERROR)

                    if error_type != self.devices.NO_ERROR:
                        self.errorHandler.add_error(
                            error_type,
                            *self.scanner.get_line_details(
                                not_dict['line_number']))
                        break
        else:
            raise Exception("Expected a NOT symbol")
            # this exception is raised to the programmer not the user

    def _switch(self):
        """Parses and executes a switch command"""
        class SwitchHolder:
            """Holds on to the details of a single switch"""

            def __init__(self, name_id, binary_digit, loop=False,
                         index1=None, index2=None, line_number=None):
                self.name_id = name_id
                self.binary_digit = binary_digit
                self.loop = loop

                self.line_number = line_number

                if loop:
                    self.index1 = index1
                    self.index2 = index2

        def _get_flat_list(switch_holder):
            """Converts the Holder into a list of dictionaries containing its
            attributes"""
            # check for loop
            if switch_holder.loop:
                flat_list = []
                for index in range(switch_holder.index1,
                                   switch_holder.index2 + 1):
                    org_name = self.names.get_name_string(
                        switch_holder.name_id)
                    # creating new_names using index
                    new_name = org_name + str(index)
                    # assigning IDs in new_names
                    [new_name_id] = self.names.lookup([new_name])
                    # list of dictionaries
                    flat_list.append({
                        'id': new_name_id,
                        'binary_digit': switch_holder.binary_digit,
                        'line_number': switch_holder.line_number})
                return flat_list
            else:
                return [{'id': switch_holder.name_id,
                         'binary_digit': switch_holder.binary_digit,
                         'line_number': switch_holder.line_number}]

        def _single_switch():
            """Parse and extract details of a single switch"""
            name_id, line_number = self._name()
            # initialise variables
            loop = False
            index1 = None
            index2 = None

            # if there is '[' then it uses loop
            if self.symbol.type == self.scanner.OPEN_SQUARE_BRACKET:
                loop = True

                self.symbol = self.scanner.get_symbol()
                index1, index2 = self._loop_times()
                self._is_close_square_bracket()

            self._is_equals()

            binary_digit = self._binary_digit()

            # returns an object with switch information
            return SwitchHolder(name_id, binary_digit, loop,
                                index1, index2, line_number)

        if(self.symbol.type == self.scanner.KEYWORD and
           self.symbol.id == self.scanner.SWITCH_ID):
            # print('SWITCH')
            self.symbol = self.scanner.get_symbol()

            switch_list = []
            # SwitchHolder object
            switch_holder = _single_switch()
            if not self.errorHandler.loc_err:
                # list of dictionaries
                switch_list.extend(_get_flat_list(switch_holder))

            # check for local error
            self.errorHandler.loc_err = False
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()

                switch_holder = _single_switch()
                if not self.errorHandler.loc_err:
                    switch_list.extend(_get_flat_list(switch_holder))

                self.errorHandler.loc_err = False

            self.errorHandler.loc_err = False
            self._is_semicolon()     # do something with the error

            self.errorHandler.loc_err = False

            if self.errorHandler.syntax_error_count == 0:
                for sw_dict in switch_list:
                    error_type = self.devices.make_device(
                        sw_dict['id'],
                        self.devices.SWITCH,
                        sw_dict['binary_digit'])

                    if error_type != self.devices.NO_ERROR:
                        self.errorHandler.add_error(
                            error_type,
                            *self.scanner.get_line_details(
                                sw_dict['line_number']))
                        break
        else:
            raise Exception("Expected a SWITCH symbol")

    def _connectlist(self, circ_name=None):
        """Parses and executes a connect command"""
        class ConnectHolder():
            """Holds on to the details of a single connection"""

            def __init__(self, input_name_id, input_port_id, input_line_number,
                         output_name_id, output_port_id, output_line_number,
                         circ_name=None):
                self.input_name_id = input_name_id
                self.input_port_id = input_port_id
                self.input_line_number = input_line_number
                self.output_name_id = output_name_id
                self.output_port_id = output_port_id
                self.output_line_number = output_line_number

                self.circ_name = circ_name

        def _get_flat_list(connect_holder):
            """Converts the Holder into a list of dictionaries containing its
            attributes"""

            input_name_id = connect_holder.input_name_id
            output_name_id = connect_holder.output_name_id

            if connect_holder.circ_name is not None:
                circ = self.names.get_name_string(
                    connect_holder.circ_name)

                input_name = self.names.get_name_string(
                    connect_holder.input_name_id)
                output_name = self.names.get_name_string(
                    connect_holder.output_name_id)

                input_name = circ + '_' + input_name
                output_name = circ + '_' + output_name

                [input_name_id] = self.names.lookup([input_name])
                [output_name_id] = self.names.lookup([output_name])

            return [{'input_id': input_name_id,
                     'input_port': connect_holder.input_port_id,
                     'input_line': connect_holder.input_line_number,
                     'output_id': output_name_id,
                     'output_port': connect_holder.output_port_id,
                     'output_line': connect_holder.output_line_number}]

        def _connection(circ_name=None):
            """Parse and extract details of a single connection"""
            input_name_id, input_port_id, input_line_number = self._signame()
            self._is_connection()
            output_name_id, output_port_id, \
                output_line_number = self._signame()
            return (ConnectHolder(input_name_id, input_port_id,
                                  input_line_number, output_name_id,
                                  output_port_id, output_line_number,
                                  circ_name))

        if(self.symbol.type == self.scanner.KEYWORD and
           self.symbol.id == self.scanner.CONNECT_ID):
            self.symbol = self.scanner.get_symbol()
            connection_list = []

            connection_holder = _connection(circ_name)
            if not self.errorHandler.loc_err:
                connection_list.extend(_get_flat_list(connection_holder))

            self.errorHandler.loc_err = False
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()

                connection_holder = _connection(circ_name)
                if not self.errorHandler.loc_err:
                    connection_list.extend(_get_flat_list(connection_holder))

                self.errorHandler.loc_err = False

            self.errorHandler.loc_err = False
            self._is_semicolon()

            self.errorHandler.loc_err = False
            if self.errorHandler.syntax_error_count == 0:
                for connection_dict in connection_list:
                    if connection_dict['input_id'] in \
                            self.devices.circuit_dict:

                        circuitHolder = self.devices.circuit_dict[
                            connection_dict['input_id']]


                        device_dict = circuitHolder.outputs[
                            connection_dict['input_port']]

                        connection_dict['input_id'] =\
                            device_dict['device_name']
                        connection_dict['input_port'] =\
                            device_dict['device_port']


                    if(connection_dict['output_id'] in
                       self.devices.circuit_dict):

                        circuitHolder = self.devices.circuit_dict[
                            connection_dict['output_id']]

                        device_dict_list = circuitHolder.inputs[
                            connection_dict['output_port']]

                        for device_dict in device_dict_list:
                            connection_dict['output_id'] =\
                                device_dict['device_name']
                            connection_dict['output_port'] =\
                                device_dict['device_port']

                            error_type = self.network.make_connection(
                                connection_dict['input_id'],
                                connection_dict['input_port'],
                                connection_dict['output_id'],
                                connection_dict['output_port'])

                            print('connection:',
                                  self.names.get_name_string(
                                      connection_dict['input_id']),
                                  'to', self.names.get_name_string(
                                      connection_dict['output_id']),
                                  'error:',
                                  error_type != self.network.NO_ERROR,
                                  error_type - self.network.NO_ERROR)

                            if connection_dict['input_port'] is not None:
                                print('input port:',
                                      self.names.get_name_string(
                                          connection_dict['input_port']))
                            if connection_dict['output_port'] is not None:
                                print('output port:',
                                      self.names.get_name_string(
                                          connection_dict['output_port']))

                            print('brrrrrrruh')
                            if error_type != self.network.NO_ERROR:
                                self.errorHandler.add_error(
                                    error_type,
                                    *self.scanner.get_line_details(
                                        connection_dict['input_line']))
                                break

                        continue


                    error_type = self.network.make_connection(
                        connection_dict['input_id'],
                        connection_dict['input_port'],
                        connection_dict['output_id'],
                        connection_dict['output_port'])

                    print('connection:',
                          self.names.get_name_string(
                              connection_dict['input_id']),
                          'to', self.names.get_name_string(
                              connection_dict['output_id']),
                          'error:', error_type != self.network.NO_ERROR,
                          error_type - self.network.NO_ERROR)

                    if connection_dict['input_port'] is not None:
                        print('input port:',
                              self.names.get_name_string(
                                  connection_dict['input_port']))
                    if connection_dict['output_port'] is not None:
                        print('output port:',
                              self.names.get_name_string(
                                  connection_dict['output_port']))

                    if error_type != self.network.NO_ERROR:
                        self.scanner.fileHandler.current_index =\
                            self.symbol.current_index
                        self.errorHandler.add_error(
                            error_type,
                            *self.scanner.get_line_details(
                                connection_dict['input_line']),
                            opt_cur_index=self.symbol.current_index)
                        break
        else:
            raise Exception("Expected a CONNECT symbol")

    def _xor_list(self, circ_name=None):
        """Parses and executes a XOR command"""
        class XorHolder():
            """Holds on to the details of a single XOR"""

            def __init__(self, name_id, loop=False,
                         index1=None, index2=None, line_number=None,
                         circ_name=None):
                self.name_id = name_id
                self.loop = loop

                self.line_number = line_number

                if self.loop:
                    self.index1 = index1
                    self.index2 = index2

                self.circ_name = circ_name

        def _get_flat_list(xor_holder):
            """Converts the Holder into a list of dictionaries containing its
            attributes"""
            flat_list = []
            if xor_holder.loop:
                for index in range(xor_holder.index1, xor_holder.index2 + 1):
                    xor_name = self.names.get_name_string(xor_holder.name_id)
                    new_name = xor_name + str(index)

                    if xor_holder.circ_name is not None:
                        circ = self.names.get_name_string(
                            xor_holder.circ_name)
                        new_name = circ + '_' + new_name

                    [new_name_id] = self.names.lookup([new_name])
                    flat_list.append({'id': new_name_id,
                                      'line_number': xor_holder.line_number})
                return flat_list
            else:
                name_id = xor_holder.name_id
                if xor_holder.circ_name is not None:
                    name = self.names.get_name_string(
                        xor_holder.name_id)
                    circ = self.names.get_name_string(
                        xor_holder.circ_name)
                    name = circ + '_' + name
                    [name_id] = self.names.lookup([name])

                return [{'id': name_id,
                         'line_number': xor_holder.line_number}]

        def _xor_gate(circ_name=None):
            """Parse and extract details of a single XOR"""
            name_id, line_number = self._name()

            loop = False
            index1 = None
            index2 = None

            if self.symbol.type == self.scanner.OPEN_SQUARE_BRACKET:
                loop = True
                self.symbol = self.scanner.get_symbol()
                index1, index2 = self._loop_times()
                self._is_close_square_bracket()

            return XorHolder(name_id, loop, index1, index2,
                             line_number, circ_name)

        if(self.symbol.type == self.scanner.KEYWORD and
           self.symbol.id == self.scanner.XOR_ID):
            self.symbol = self.scanner.get_symbol()

            xor_list = []
            xor_holder = _xor_gate(circ_name)
            if not self.errorHandler.loc_err:
                xor_list.extend(_get_flat_list(xor_holder))

            self.errorHandler.loc_err = False
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                xor_holder = _xor_gate(circ_name)

                if not self.errorHandler.loc_err:
                    xor_list.extend(_get_flat_list(xor_holder))

                self.errorHandler.loc_err = False

            self.errorHandler.loc_err = False
            self._is_semicolon()

            self.errorHandler.loc_err = False

            if self.errorHandler.syntax_error_count == 0:
                error_type_list = []
                for xor_dict in xor_list:
                    error_type = self.devices.make_device(xor_dict['id'],
                                                          self.devices.XOR)

                    print('XOR', self.names.get_name_string(xor_dict['id']),
                          'error:', error_type != self.devices.NO_ERROR,
                          error_type - self.devices.NO_ERROR)

                    error_type_list.append(error_type)

                    if error_type != self.devices.NO_ERROR:
                        self.errorHandler.add_error(
                            error_type, *self.scanner.get_line_details(
                                xor_dict['line_number']))
                        break
        else:
            raise Exception("Expected a XOR symbol")

    def _monitor_list(self):
        """Parses and execute a monitors command"""
        class MonitorHolder():
            """Holds on to the details of a single monitor"""

            def __init__(self, device_name_id, output_port_id, line_number):
                self.device_name_id = device_name_id
                self.output_port_id = output_port_id
                self.line_number = line_number

        def _get_flat_list(monitor_holder):
            """Converts the Holder into a list of dictionaries containing its
            attributes"""
            return [{'device_id': monitor_holder.device_name_id,
                     'output_port': monitor_holder.output_port_id,
                     'line_number': monitor_holder.line_number}]

        if(self.symbol.type == self.scanner.KEYWORD and
           self.symbol.id == self.scanner.MONITOR_ID):
            # print('MONITOR')
            self.symbol = self.scanner.get_symbol()

            monitor_list = []
            device_name_id, output_port_id, line_number = self._signame()
            monitor_holder = MonitorHolder(device_name_id,
                                           output_port_id, line_number)
            if not self.errorHandler.loc_err:
                monitor_list.extend(_get_flat_list(monitor_holder))

            self.errorHandler.loc_err = False
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()

                device_name_id, output_port_id, line_number = self._signame()
                monitor_holder = MonitorHolder(device_name_id,
                                               output_port_id, line_number)

                if not self.errorHandler.loc_err:
                    monitor_list.extend(_get_flat_list(monitor_holder))

                self.errorHandler.loc_err = False

            self.errorHandler.loc_err = False
            self._is_semicolon()

            self.errorHandler.loc_err = False

            if self.errorHandler.syntax_error_count == 0:
                for monitor_dict in monitor_list:

                    if monitor_dict['device_id'] in self.devices.circuit_dict:
                        circuitHolder = self.devices.circuit_dict[
                            monitor_dict['device_id']]


                        device_dict =\
                            circuitHolder.outputs[monitor_dict['output_port']]

                        monitor_dict['device_id'] =\
                            device_dict['device_name']
                        monitor_dict['output_port'] =\
                            device_dict['device_port']

                    error_type = self.monitors.make_monitor(
                        monitor_dict['device_id'], monitor_dict['output_port'])


                    if error_type != self.monitors.NO_ERROR:
                        self.errorHandler.add_error(
                            error_type, *self.scanner.get_line_details(
                                monitor_dict['line_number']))
                        break

        else:
            raise Exception("Expected a MONITOR symbol")

    def _clock(self):
        """Parses and execute a clocks command"""
        class ClockHolder():
            """Holds on to the details of a single clock"""

            def __init__(self, name_id, period, loop=False,
                         index1=None, index2=None, line_number=None):
                self.name_id = name_id
                self.loop = loop
                self.period = period

                self.line_number = line_number

                if self.loop:
                    self.index1 = index1
                    self.index2 = index2

        def _get_flat_list(clock_holder):
            """Converts the Holder into a list of dictionaries containing its
            attributes"""
            flat_list = []
            if clock_holder.loop:
                for index in range(clock_holder.index1,
                                   clock_holder.index2 + 1):
                    clock_name = self.names.get_name_string(
                        clock_holder.name_id)
                    new_name = clock_name + str(index)
                    [new_name_id] = self.names.lookup([new_name])
                    flat_list.append({'id': new_name_id,
                                      'period': clock_holder.period,
                                      'line_number': clock_holder.line_number})
                return flat_list
            else:
                return [{'id': clock_holder.name_id,
                         'period': clock_holder.period,
                         'line_number': clock_holder.line_number}]

        def _single_clock():
            """Parse and extract details of a single clock"""
            name_id, line_number = self._name()
            loop = False
            index1 = None
            index2 = None

            if self.symbol.type == self.scanner.OPEN_SQUARE_BRACKET:
                loop = True
                self.symbol = self.scanner.get_symbol()
                self._loop_times()
                self._is_close_square_bracket()
            input_period = self._input_period()
            return (ClockHolder(name_id, input_period, loop,
                                index1, index2, line_number))

        if(self.symbol.type == self.scanner.KEYWORD and
                self.symbol.id == self.scanner.CLOCK_ID):
            self.symbol = self.scanner.get_symbol()

            clock_list = []

            clock_holder = _single_clock()
            if not self.errorHandler.loc_err:
                clock_list.extend(_get_flat_list(clock_holder))

            self.errorHandler.loc_err = False
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                clock_holder = _single_clock()

                if not self.errorHandler.loc_err:
                    clock_list.extend(_get_flat_list(clock_holder))

                self.errorHandler.loc_err = False

            self.errorHandler.loc_err = False
            self._is_semicolon()     

            self.errorHandler.loc_err = False

            if self.errorHandler.syntax_error_count == 0:
                for clock_dict in clock_list:
                    error_type = self.devices.make_device(
                        clock_dict['id'], self.devices.CLOCK,
                        clock_dict['period'])


                    if error_type != self.devices.NO_ERROR:
                        self.errorHandler.add_error(
                            error_type,
                            *self.scanner.get_line_details(
                                clock_dict['line_number']))
                        break

        else:
            raise Exception("Expected a CLOCK symbol")

    def _gate_list(self, circ_name=None):
        """Parses and executes a gate command (AND, NAND, OR, NOR)"""
        class GateHolder:
            """Holds on to the details of a single gate"""

            def __init__(self, name_id, input_pins, loop=False,
                         index1=None, index2=None, line_number=None,
                         circ_name=None):
                self.name_id = name_id
                self.loop = loop
                self.input_pins = input_pins

                self.line_number = line_number

                if self.loop:
                    self.index1 = index1
                    self.index2 = index2

                self.circ_name = circ_name

        def _get_flat_list(gate_holder):
            """Converts the Holder into a list of dictionaries containing its
            attributes"""
            flat_list = []
            if gate_holder.loop:
                for index in range(gate_holder.index1, gate_holder.index2 + 1):
                    gate_name = self.names.get_name_string(gate_holder.name_id)
                    new_name = gate_name + str(index)

                    if gate_holder.circ_name is not None:
                        circ = self.names.get_name_string(
                            gate_holder.circ_name)
                        new_name = circ + '_' + new_name

                    [new_name_id] = self.names.lookup([new_name])
                    flat_list.append({'id': new_name_id,
                                      'inputs': gate_holder.input_pins,
                                      'line_number': gate_holder.line_number})
                return flat_list
            else:
                name_id = gate_holder.name_id
                if gate_holder.circ_name is not None:
                    name = self.names.get_name_string(
                        gate_holder.name_id)
                    circ = self.names.get_name_string(
                        gate_holder.circ_name)
                    name = circ + '_' + name
                    [name_id] = self.names.lookup([name])

                return [{'id': name_id,
                         'inputs': gate_holder.input_pins,
                         'line_number': gate_holder.line_number}]

        def _gate(circ_name=None):
            """Parse and extract details of a single gate"""
            name_id, line_number = self._name()
            loop = False
            index1 = None
            index2 = None

            if self.symbol.type == self.scanner.OPEN_SQUARE_BRACKET:
                loop = True

                self.symbol = self.scanner.get_symbol()
                index1, index2 = self._loop_times()
                self._is_close_square_bracket()

            input_pins = self._pin_input()

            return GateHolder(name_id, input_pins, loop,
                              index1, index2, line_number, circ_name)

        print(self.symbol.val)
        if(self.symbol.type == self.scanner.KEYWORD and
           self.symbol.id in [self.scanner.AND_ID, self.scanner.OR_ID,
                              self.scanner.NAND_ID, self.scanner.NOR_ID]):
            print('GATE:', self.symbol.val)

            device_mapping = {
                self.scanner.AND_ID: self.devices.AND,
                self.scanner.OR_ID: self.devices.OR,
                self.scanner.NAND_ID: self.devices.NAND,
                self.scanner.NOR_ID: self.devices.NOR,
            }
            device_kind = device_mapping[self.symbol.id]

            self.symbol = self.scanner.get_symbol()

            gate_list = []

            gate_holder = _gate(circ_name)
            if not self.errorHandler.loc_err:
                gate_list.extend(_get_flat_list(gate_holder))

            self.errorHandler.loc_err = False
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()
                gate_holder = _gate(circ_name)

                if not self.errorHandler.loc_err:
                    gate_list.extend(_get_flat_list(gate_holder))

                self.errorHandler.loc_err = False

            self.errorHandler.loc_err = False
            self._is_semicolon()

            self.errorHandler.loc_err = False

            if self.errorHandler.syntax_error_count == 0:
                error_type_list = []
                for gate_dict in gate_list:
                    if gate_dict['inputs'] < 1 or gate_dict['inputs'] > 16:
                        self.errorHandler.add_error(
                            self.errorHandler.semantic.INVALID_PINS,
                            *self.scanner.get_line_details(
                                gate_dict['line_number']))
                        break

                    error_type = self.devices.make_device(
                        gate_dict['id'], device_kind, gate_dict['inputs'])

                    print(self.names.get_name_string(device_kind),
                          self.names.get_name_string(gate_dict['id']),
                          'inputs:', gate_dict['inputs'],
                          'error:', error_type != self.devices.NO_ERROR,
                          error_type - self.devices.NO_ERROR)

                    error_type_list.append(error_type)
                    if error_type != self.devices.NO_ERROR:
                        self.errorHandler.add_error(
                            error_type,
                            *self.scanner.get_line_details(
                                gate_dict['line_number']))
                        break
        else:
            raise Exception("Expected a GATE symbol")

    def _dtype(self, circ_name=None):
        """Parses and executes a dtype command"""
        class DtypeHolder:
            """Holds on to the details of a single dtype"""

            def __init__(self, name_id, loop=False,
                         index1=None, index2=None, line_number=None,
                         circ_name=None):
                self.name_id = name_id
                self.loop = loop

                self.line_number = line_number

                if loop:
                    self.index1 = index1
                    self.index2 = index2

                self.circ_name = circ_name

        def _get_flat_list(dtype_holder):
            """Converts the Holder into a list of dictionaries containing its
            attributes"""
            if dtype_holder.loop:
                flat_list = []
                for index in range(dtype_holder.index1,
                                   dtype_holder.index2 + 1):
                    org_name = self.names.get_name_string(dtype_holder.name_id)
                    new_name = org_name + str(index)

                    if dtype_holder.circ_name is not None:
                        circ = self.names.get_name_string(
                            dtype_holder.circ_name)
                        new_name = circ + '_' + new_name

                    [new_name_id] = self.names.lookup([new_name])
                    flat_list.append({'id': new_name_id,
                                      'line_number': dtype_holder.line_number})
                return flat_list
            else:
                name_id = dtype_holder.name_id
                if dtype_holder.circ_name is not None:
                    name = self.names.get_name_string(
                        dtype_holder.name_id)
                    circ = self.names.get_name_string(
                        dtype_holder.circ_name)
                    name = circ + '_' + name
                    [name_id] = self.names.lookup([name])
                return [{'id': name_id,
                         'line_number': dtype_holder.line_number}]

        def _single_dtype(circ_name=None):
            """Parse and extract details of a single dtype"""
            name_id, line_number = self._name()
            loop = False
            index1 = None
            index2 = None

            if self.symbol.type == self.scanner.OPEN_SQUARE_BRACKET:
                loop = True
                self.symbol = self.scanner.get_symbol()
                index1, index2 = self._loop_times()
                self._is_close_square_bracket()
            return DtypeHolder(name_id, loop, index1, index2, line_number,
                               circ_name)

        if(self.symbol.type == self.scanner.KEYWORD and
           self.symbol.id == self.scanner.DTYPE_ID):
            self.symbol = self.scanner.get_symbol()
            dtype_list = []

            dtype_holder = _single_dtype(circ_name)
            if not self.errorHandler.loc_err:
                dtype_list.extend(_get_flat_list(dtype_holder))

            self.errorHandler.loc_err = False
            while self.symbol.type == self.scanner.COMMA:
                self.symbol = self.scanner.get_symbol()

                dtype_holder = _single_dtype(circ_name)
                if not self.errorHandler.loc_err:
                    dtype_list.extend(_get_flat_list(dtype_holder))
                self.errorHandler.loc_err = False

            self.errorHandler.loc_err = False
            self._is_semicolon()

            self.errorHandler.loc_err = False

            if self.errorHandler.syntax_error_count == 0:
                for dt_dict in dtype_list:
                    error_type = self.devices.make_device(dt_dict['id'],
                                                          self.devices.D_TYPE)

                    print('Dtype:', self.names.get_name_string(dt_dict['id']))

                    if error_type != self.devices.NO_ERROR:
                        self.errorHandler.add_error(
                            error_type,
                            *self.scanner.get_line_details(
                                dt_dict['line_number']))
                        break

        else:
            raise Exception("Expected a GATE symbol")

    # ----------------------------------------------------------------------- #

    def _skip_to_stopping_symbol(self):
        """Skips to the next stopping symbol"""
        while self.symbol.type not in self.stopping_symbols:
            self.symbol = self.scanner.get_symbol()

        return self.symbol

    # ----------------------------------------------------------------------- #

    def _name(self):
        """Checks if current symbol is a name and returns it"""
        if not self.errorHandler.loc_err:
            print('name:', self.symbol.val)
            name_id = self.symbol.id
            line_number = self.symbol.line_number
            self.symbol = self.scanner.get_symbol()

            self._is_it_name(name_id)

            return name_id, line_number
        return None

    def _port(self):
        """Returns the port"""
        if not self.errorHandler.loc_err:
            print('port:', self.symbol.val)
            port_id = self.symbol.id

            self.symbol = self.scanner.get_symbol()

            return port_id
        return None

    def _signame(self):
        """Returns the signame (signal and port)"""
        if not self.errorHandler.loc_err:
            name_id, line_number = self._name()
            print('signame:', self.symbol.val)

            port_id = None

            if self.symbol.type == self.scanner.FULLSTOP:
                self.symbol = self.scanner.get_symbol()
                port_id = self._port()


            return name_id, port_id, line_number

        return None, None, None

    def _number(self):
        """Checks if current symbol is a number and returns it"""
        if not self.errorHandler.loc_err:
            if self.symbol.type == self.scanner.NUMBER:
                print('number:', self.symbol.val)
                number_id = self.symbol.id

                self.symbol = self.scanner.get_symbol()

                return number_id
            else:

                self.errorHandler.loc_err = True
                self.errorHandler.add_error(
                    self.errorHandler.syntax.NOT_NUMBER,
                    *self.scanner.get_line_details()
                )

                self.symbol = self._skip_to_stopping_symbol()
        return None

    def _pin_input(self):
        """Parses the number of inputs"""
        self._is_open_parenthesis()
        self._is_in()
        self._is_equals()
        num = self._number()
        self._is_close_parenthesis()
        return num

    def _input_period(self):
        """Parses the number of period"""
        self._is_open_parenthesis()
        self._is_period()
        self._is_equals()
        num = self._number()
        self._is_close_parenthesis()
        return num

    def _binary_digit(self):
        """Checks if the current symbol is a binary digit and returns it"""
        if not self.errorHandler.loc_err:
            if self.symbol.type == self.scanner.NUMBER:
                if self.symbol.id == 0 or self.symbol.id == 1:
                    print('binarydigit:', self.symbol.val)
                    binary_digit_id = self.symbol.id

                    self.symbol = self.scanner.get_symbol()

                    return binary_digit_id
                else:

                    self.errorHandler.loc_err = True
                    self.errorHandler.add_error(
                        self.errorHandler.syntax.NOT_BINARY_DIGIT,
                        *self.scanner.get_line_details()
                    )

                    self.symbol = self._skip_to_stopping_symbol()
            else:

                self.errorHandler.loc_err = True
                self.errorHandler.add_error(
                    self.errorHandler.syntax.NOT_BINARY_DIGIT,
                    *self.scanner.get_line_details()
                )

                self.symbol = self._skip_to_stopping_symbol()
            return None

    def _loop_times(self):
        """Parses the name loop and returns the indices"""
        index1 = self._number()
        self._is_to()
        index2 = self._number()

        if not self.errorHandler.loc_err:
            if index1 > index2:

                self.errorHandler.loc_err = True
                self.errorHandler.add_error(
                    self.errorHandler.semantic.LOOP_INDEX_BAD_ORDER,
                    *self.scanner.get_line_details()
                )

                self.symbol = self._skip_to_stopping_symbol()

                return None, None
            else:
                return index1, index2

        return None, None

    # ----------------------------------------------------------------------- #

    def _is_it_name(self, name_id):
        """Checks if name_id corresponds to a valid name"""
        if not self.errorHandler.loc_err:
            if name_id is not None:
                name = self.names.get_name_string(name_id)
                if((not name[0].isalpha()) or (not name.isalnum())):

                    self.errorHandler.loc_err = True
                    self.errorHandler.add_error(
                        self.errorHandler.syntax.NOT_NAME,
                        *self.scanner.get_line_details()
                    )

                    self.symbol = self._skip_to_stopping_symbol()
                    return False
                elif name in self.scanner.keywords_list:

                    self.errorHandler.add_error(
                        self.errorHandler.syntax.RESERVED_NAME,
                        *self.scanner.get_line_details()
                    )

                    self.symbol = self._skip_to_stopping_symbol()
                    return False
                else:
                    return True
            else:

                self.errorHandler.loc_err = True
                self.errorHandler.add_error(
                    self.errorHandler.syntax.NOT_NAME,
                    *self.scanner.get_line_details()
                )
                self.symbol = self._skip_to_stopping_symbol()
        return False

    def _is_equals(self):
        """Checks if the current symbol is an equals"""
        if not self.errorHandler.loc_err:
            if self.symbol.type == self.scanner.EQUALS:
                print('equals:', self.symbol.val)
                self.symbol = self.scanner.get_symbol()
                return True
            else:

                self.errorHandler.loc_err = True
                self.errorHandler.add_error(
                    self.errorHandler.syntax.MISSING_EQUALS,
                    *self.scanner.get_line_details()
                )
                self.symbol = self._skip_to_stopping_symbol()
                return False
        return False

    def _is_comma(self):
        """Checks if the current symbol is a comma"""
        if not self.errorHandler.loc_err:
            if self.symbol.type == self.scanner.COMMA:
                print('COMMA:', self.symbol.val)
                self.symbol = self.scanner.get_symbol()
                return True
            else:

                self.errorHandler.loc_err = True
                self.errorHandler.add_error(
                    self.errorHandler.syntax.MISSING_COMMA,
                    *self.scanner.get_line_details()
                )
                self.symbol = self._skip_to_stopping_symbol()
                return False
        return False

    def _is_semicolon(self):
        """Checks if the current symbol is an semicolon"""
        if not self.errorHandler.loc_err:
            if self.symbol.type == self.scanner.SEMICOLON:
                print('semicolon:', self.symbol.val)
                self.symbol = self.scanner.get_symbol()
                return True
            else:

                self.errorHandler.loc_err = True
                self.errorHandler.add_error(
                    self.errorHandler.syntax.MISSING_SEMICOLON,
                    *self.scanner.get_line_details()
                )

                self.symbol = self._skip_to_stopping_symbol()

                return False
        return False

    def _is_close_square_bracket(self):
        """Checks if the current symbol is a ']' closed square bracket"""
        if not self.errorHandler.loc_err:
            if self.symbol.type == self.scanner.CLOSE_SQUARE_BRACKET:
                print('closesqbracket:', self.symbol.val)
                self.symbol = self.scanner.get_symbol()
                return True
            else:

                self.errorHandler.loc_err = True
                self.errorHandler.add_error(
                    self.errorHandler.syntax.MISSING_CLOSE_SQUARE_BRACKET,
                    *self.scanner.get_line_details()
                )

                self.symbol = self._skip_to_stopping_symbol()

                return False
        return False

    def _is_to(self):
        """Checks if the current symbol is a TO"""
        if not self.errorHandler.loc_err:
            if self.symbol.type == self.scanner.TO:
                print('TO:', self.symbol.val)
                self.symbol = self.scanner.get_symbol()
                return True
            else:

                self.errorHandler.loc_err = True
                self.errorHandler.add_error(
                    self.errorHandler.syntax.MISSING_TO,
                    *self.scanner.get_line_details()
                )

                self.symbol = self._skip_to_stopping_symbol()
                return False
        return False

    def _is_connection(self):
        """Checks if the current symbol is a '->' connection"""
        if not self.errorHandler.loc_err:
            if self.symbol.type == self.scanner.CONNECTION:
                self.symbol = self.scanner.get_symbol()
                return True
            else:

                self.errorHandler.loc_err = True
                self.errorHandler.add_error(
                    self.errorHandler.syntax.MISSING_CONNECTION,
                    *self.scanner.get_line_details()
                )

                self.symbol = self._skip_to_stopping_symbol()
                return False
        return False

    def _is_open_parenthesis(self):
        """Checks if the current symbol is a '(' open parenthesis"""
        if not self.errorHandler.loc_err:
            if self.symbol.type == self.scanner.OPEN_PARENTHESIS:
                print('openparenthesis:', self.symbol.val)
                self.symbol = self.scanner.get_symbol()
                return True
            else:

                self.errorHandler.loc_err = True
                self.errorHandler.add_error(
                    self.errorHandler.syntax.MISSING_OPEN_PARENTHESIS,
                    *self.scanner.get_line_details()
                )

                self.symbol = self._skip_to_stopping_symbol()
                return False
        return False

    def _is_close_parenthesis(self):
        """Checks if the current symbol is a ')' close parenthesis"""
        if not self.errorHandler.loc_err:
            if self.symbol.type == self.scanner.CLOSE_PARENTHESIS:
                print('closesparenthesis:', self.symbol.val)
                self.symbol = self.scanner.get_symbol()
                return True
            else:

                self.errorHandler.loc_err = True
                self.errorHandler.add_error(
                    self.errorHandler.syntax.MISSING_CLOSE_PARENTHESIS,
                    *self.scanner.get_line_details()
                )

                self.symbol = self._skip_to_stopping_symbol()
                return False
        return False

    def _is_open_curly_bracket(self):
        """Checks if the current symbol is a '{' open curly brace"""
        if not self.errorHandler.loc_err:
            if self.symbol.type == self.scanner.OPEN_CURLY_BRACKET:
                print('opencurlybracket:', self.symbol.val)
                self.symbol = self.scanner.get_symbol()
                return True
            else:

                self.errorHandler.loc_err = True
                self.errorHandler.add_error(
                    self.errorHandler.syntax.MISSING_OPEN_CURLY_BRACKET,
                    *self.scanner.get_line_details()
                )

                self.symbol = self._skip_to_stopping_symbol()
                return False
        return False

    def _is_close_curly_bracket(self):
        """Checks if the current symbol is a '}' close curly brace"""
        if not self.errorHandler.loc_err:
            print(1515151515)
            if self.symbol.type == self.scanner.CLOSE_CURLY_BRACKET:
                print('closecurlybracket:', self.symbol.val)
                self.symbol = self.scanner.get_symbol()
                return True
            else:

                self.errorHandler.loc_err = True
                self.errorHandler.add_error(
                    self.errorHandler.syntax.MISSING_CLOSE_CURLY_BRACKET,
                    *self.scanner.get_line_details()
                )

                self.symbol = self._skip_to_stopping_symbol()
                return False
        return False

    def _is_in(self):
        """Checks if the current symbol is a IN"""
        if not self.errorHandler.loc_err:
            if self.symbol.type == self.scanner.IN:
                print('IN:', self.symbol.val)
                self.symbol = self.scanner.get_symbol()
                return True
            else:

                self.errorHandler.loc_err = True
                self.errorHandler.add_error(
                    self.errorHandler.syntax.MISSING_IN,
                    *self.scanner.get_line_details()
                )

                self.symbol = self._skip_to_stopping_symbol()
                return False
        return False

    def _is_period(self):
        """Checks if the current symbol is a PERIOD"""
        if not self.errorHandler.loc_err:
            if self.symbol.type == self.scanner.PERIOD:
                self.symbol = self.scanner.get_symbol()
                return True
            else:

                self.errorHandler.loc_err = True
                self.errorHandler.add_error(
                    self.errorHandler.syntax.MISSING_PERIOD,
                    *self.scanner.get_line_details()
                )

                self.symbol = self._skip_to_stopping_symbol()
                return False
        return False
