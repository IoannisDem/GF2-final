# GF2 Software - Logic Simulator, Team 17

Logic simulator program built for the IIA CUED GF2 Software project.
Simulates simple circuits by reading a logic description language .vi file provided. Displays traces of specified signals (monitors) for a number of cycles. Switches can be turned on/off during operation, while monitors and circuit connections can also be modified.
Built to support the following circuit devices: NOT, AND, NAND, OR, NOR, XOR gates, CIRCUIT; switches; d-type flip flops; clocks
Developed and tested on both Linux and Windows 10.
Available in English (en_US.utf8) and Greek (el_GR.utf8).

## INSTALLATION REQUIREMENTS - LINUX (UBUNTU 20.04)
- Python 3 (any version, tested on Python 3.6.0)
- Python 3 OpenGL
- Python 3 wxWidgets (i.e. wxPython) - wxgtx4.0
- GLUT - freeglut3-dev
Note that in an Anaconda shell most of the above are installed by default in the testing machines (DPO). The main requirement is to ensure that Python 3 is used for the execution.

## SET-UP INSTRUCTIONS
Ensure you follow the given instructions to run this program:
1. Set up an Anaconda environment, such as by loading an appropriate Anaconda terminal.
2. Navigate to the directory of the installed software (in the terminal): "cd .../final/logsim".
3. Execute the system by running: "python3 logsim.py FILENAME.vi" where FILENAME is the name of the LDL file located in the definition_files directory. A few description files are available by default.

## DEVIATIONS FROM PEP8
- Within the GUI.py module, wxPython event methods are designable as non-public methods, since they only apply to their specific frame. However, usual convention is to call each method as "on_button(self, event)" instead
of "_button(self, event)". Furthermore, event is always passed as a parameter even if it is not called within the method.

## AUTHORS
Yash Gaikwad, ysg22
Richard Marques Monteiro, rm967
Ioannis Demetriades, id350