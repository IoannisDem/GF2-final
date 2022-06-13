# -*- coding: utf-8 -*-
"""
Created on Tue May 24 15:39:41 2022

@author: Yash
"""

from scanner import Scanner
from names import Names
from parse import Parser
from error_handling import ErrorHandler
from devices import Devices
from network import Network
from monitors import Monitors

path = 'circ.vi'
names = Names()
errorHandler = ErrorHandler(names)

scanner = Scanner(path, names)      # pass error handler here too!!!!!!!
devices = Devices(names, errorHandler)
network = Network(names,devices,errorHandler)
monitors = Monitors(names, devices, network, errorHandler)



parser = Parser(names, devices, network, monitors, scanner, errorHandler)

parser.parse_network()
# parser.errorHandler.display_errors()
# print('doneeeeeeeeee: ',parser.errorHandler.error_list[0].error_id)

'''
TODO for circuit,

what if youi don't specify all inputs?

when you monitor, but forget to specify port
MONITOR jk1, instead of jk1.O1;

what if you have jk bistable where clock is connected to two places?
'''