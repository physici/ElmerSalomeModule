import sys
from PyQt4 import QtGui
from PyQt4 import QtXml
from PyQt4 import QtCore

import elmer_window_handler

sp = None
 
def equation():
    global sp
    sp = ewh.showAddEquation()    
 
# Create the Qt Application
app = QtGui.QApplication(sys.argv)
# Create a button, connect it and show it
button = QtGui.QPushButton("Click me")
ewh = elmer_window_handler.elmerWindowHandler()
button.clicked.connect(equation)
button.show()
# Run the main Qt loop
app.exec_()