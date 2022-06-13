"""
Created on Tue May 31 17:48:59 2022

@author: John Demetriades
"""

import pytest
from names import Names
from parse import Parser
from error_handling import ErrorHandler
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner

names = Names()
error_Handler = ErrorHandler(names)
devices = Devices(names, error_Handler)
network = Network(names,devices,error_Handler)
monitors = Monitors(names, devices, network, error_Handler)
    
test_dev = [('SWITCH sw[1 TO 2] = 0, sw[11 TO 12] = 1;'),
             ('NAND nand100(IN = 3), nand6          (IN = 4);'),
             ('NAND nand[1 TO 2](IN = 3), nand[3 TO 4](IN = 4);'),
             ('XOR a, b[2 TO 5];'),
             ('CLOCK clk(PERIOD =           50), ck(PERIOD = 20);'),
             ('DTYPE d[1 TO 2];'),
             ('NOR not1;')
             ]

test_dev_error = [('SWITCH sw[1 TO 2]  0, sw[11 TO 12] = 1;', error_Handler.syntax.MISSING_EQUALS),
                  ('NAND nand100(= 3), nand6          (IN = 4);', error_Handler.syntax.MISSING_IN),
                  ('NAND nand[1 TO 2](IN = 3), nand[3 TO 4](IN = 4)', error_Handler.syntax.MISSING_SEMICOLON),
                  ('XOR a, b [2 TO 5;', error_Handler.syntax.MISSING_CLOSE_SQUARE_BRACKET),
                  ('CLOCK clk(PERIOD =           50;', error_Handler.syntax.MISSING_CLOSE_PARENTHESIS),
                  ('CLOCK ck( = 20);', error_Handler.syntax.MISSING_PERIOD),
                  ('CLOCK ck( PERIOD = );', error_Handler.syntax.NOT_NUMBER),
                  ('SWITCH sw[1 TO 2]  = ', error_Handler.syntax.NOT_BINARY_DIGIT)
                  ]

test_connection = [('SWITCH sw[1 TO 2] = 0; NAND nand1(IN = 2); CONNECT sw1 -> nand1.I1; CONNECT sw2 -> nand1.I2;'),
                   ('SWITCH sw[3 TO 4] = 0; NAND nand2(IN = 2); CONNECT sw3 -> nand2.I1; CONNECT sw4 -> nand2.I2;MONITOR nand.I1')
                   ]

semantic_errors = [('AND and[1 TO 2](IN = 2); CONNECT and1.I1 -> and2.I1;', network.INPUT_TO_INPUT),
                   ('OR or[1 TO 2](IN = 2); CONNECT or1-> or2;', network.OUTPUT_TO_OUTPUT),
                   ('SWITCH sw[1 TO 2] = 0; NAND nand[1 TO 2](IN = 2); CONNECT nand1-> nand2.I1; CONNECT sw1-> nand2.I1;', network.INPUT_CONNECTED),
                   ('XOR xor[1 TO 2]; CONNECT xor1 -> xor2.I3;', network.PORT_ABSENT),
                   ('NAND nand[1 TO 2](IN = 2); CONNECT nand1 -> nand3.I1;', network.DEVICE_ABSENT),
                   ('DTYPE d; CLOCK clk (PERIOD = 20); NOR nor[1 TO 2](IN=2); CONNECT clk -> d.CLK; CONNECT nor2 -> d.CLK;',network.INPUT_CONNECTED)
                   ]


@pytest.fixture
def new_objects():
    """Returns all required objects for parsing"""
    names = Names()
    error_handler = ErrorHandler(names)
    devices = Devices(names, error_handler)
    network = Network(names,devices,error_handler)
    monitors = Monitors(names, devices, network, error_handler)
    return names, error_handler, devices, network, monitors

def new_file(tmpdir, file_content):
    p = tmpdir.mkdir('sub').join('example.txt')
    p.write(file_content)
    return p

     
@pytest.mark.parametrize("device",test_dev)
def test_make_dev(device,tmpdir, new_objects):
    '''Test on making devices'''
    [names, error_Handler, devices,
     network, monitors] = new_objects
    
    path = new_file(tmpdir,device)
    scanner = Scanner(path,names)
    parser = Parser(names, devices, network, monitors, scanner, error_Handler)
    assert parser.parse_network() == True
    
@pytest.mark.parametrize("connection",test_connection)
def test_make_con(connection,tmpdir, new_objects):
    ''' Test on making connections'''
    [names, error_Handler, devices,
     network, monitors] = new_objects
    
    path = new_file(tmpdir,connection)
    scanner = Scanner(path,names)
    parser = Parser(names, devices, network, monitors, scanner, error_Handler)
    assert parser.parse_network() == True

@pytest.mark.parametrize('device,error',test_dev_error)
def test_syntax(device,error,tmpdir, new_objects):
    '''Test syntax errors'''
    [names, error_Handler, devices,
     network, monitors] = new_objects

    path = new_file(tmpdir,device)
    scanner = Scanner(path,names)
    parser = Parser(names, devices, network, monitors, scanner, error_Handler)
    parser.parse_network()
    assert parser.errorHandler.error_list[0].error_id == error
    
@pytest.mark.parametrize('connection,error',semantic_errors)
def test_semantic(connection,error,tmpdir, new_objects):
    ''' Test semantic errors'''
    [names, error_Handler, devices,
     network, monitors] = new_objects

    path = new_file(tmpdir,connection)
    scanner = Scanner(path,names)
    parser = Parser(names, devices, network, monitors, scanner, error_Handler)
    parser.parse_network()
    assert parser.errorHandler.error_list[0].error_id == error
