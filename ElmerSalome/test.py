import sys
from PyQt4 import QtGui
from PyQt4 import QtXml
from PyQt4 import QtCore

sys.dont_write_bytecode = True

import elmer_window_handler


sp = None
 
def equation():
    global sp
    sp = ewh.showAddEquation()    

def material():
    global sp
    sp = ewh.showAddMaterial()  
    
def bodyforce():
    global sp
    sp = ewh.showAddBodyForce()  

def boundary():
    global sp
    sp = ewh.showAddBoundaryCondition()    
    
def body():
    global sp
    sp = ewh.showBodyPropertyDefinition("test2")    

def initial():
    global sp
    sp = ewh.showAddInitialCondition()  

if __name__ == "__main__":
    # Create the Qt Application
    app = QtGui.QApplication(sys.argv)
    window = QtGui.QWidget()
    layout = QtGui.QVBoxLayout()
    # Create a button, connect it and show it
    button = QtGui.QPushButton("Equation")
    ewh = elmer_window_handler.elmerWindowHandler()
    button.clicked.connect(equation)
    layout.addWidget(button)
    
    button1 = QtGui.QPushButton("Material")
    ewh = elmer_window_handler.elmerWindowHandler()
    button1.clicked.connect(material)
    layout.addWidget(button1)
    
    button2 = QtGui.QPushButton("BodyForce")
    ewh = elmer_window_handler.elmerWindowHandler()
    button2.clicked.connect(bodyforce)
    layout.addWidget(button2)
    
    button3 = QtGui.QPushButton("Boundary")
    ewh = elmer_window_handler.elmerWindowHandler()
    button3.clicked.connect(boundary)
    layout.addWidget(button3)
    
    button4 = QtGui.QPushButton("Body")
    ewh = elmer_window_handler.elmerWindowHandler()
    button4.clicked.connect(body)
    layout.addWidget(button4)

    button5 = QtGui.QPushButton("Initial")
    ewh = elmer_window_handler.elmerWindowHandler()
    button5.clicked.connect(initial)
    layout.addWidget(button5)

    window.setLayout(layout)    
    window.show()    
    
    # Run the main Qt loop
    app.exec_()