import sys
from PyQt4 import QtGui
from PyQt4 import QtXml
from PyQt4 import QtCore

sys.dont_write_bytecode = True

import elmer_window_handler
import sifwrite


sp = None

def about():
    ewh.about()

def general():
    global sp
    sp = ewh.showGeneralSetup()

def equation():
    global sp
    sp = ewh.showAddEquation()    

def material():
    global sp
    sp = ewh.showAddMaterial()  
    
def boundarycondition():
    global sp
    sp = ewh.showAddBoundaryCondition()  

def bodyforce():
    global sp
    sp = ewh.showAddBodyForce()  

def boundary():
    global sp
    sp = ewh.showBoundaryPropertyDefinition("test")    
    
def body():
    global sp
    sp = ewh.showBodyPropertyDefinition("test2")    

def initial():
    global sp
    sp = ewh.showAddInitialCondition()  

def sif_write():
    print('sifwrite test')
    sifwrite.write_sif(ewh)

def start_GUI():
    global ewh
    # Create the Qt Application
    app = QtGui.QApplication(sys.argv)
    window = QtGui.QWidget()
    layout = QtGui.QVBoxLayout()

    ewh = elmer_window_handler.elmerWindowHandler()

    ewh.initGeneralSetup()

    # Create buttons, connect and show them

    button_about = QtGui.QPushButton("About")
    #ewh = elmer_window_handler.elmerWindowHandler()
    button_about.clicked.connect(about)
    layout.addWidget(button_about)

    button_general = QtGui.QPushButton("General")
    #ewh = elmer_window_handler.elmerWindowHandler()
    button_general.clicked.connect(general)
    layout.addWidget(button_general)

    button_equation = QtGui.QPushButton("Equation")
    #ewh = elmer_window_handler.elmerWindowHandler()
    button_equation.clicked.connect(equation)
    layout.addWidget(button_equation)
    
    button_material = QtGui.QPushButton("Material")
    #ewh = elmer_window_handler.elmerWindowHandler()
    button_material.clicked.connect(material)
    layout.addWidget(button_material)
    
    button_BC = QtGui.QPushButton("BoundaryCondition")
    #ewh = elmer_window_handler.elmerWindowHandler()
    button_BC.clicked.connect(boundarycondition)
    layout.addWidget(button_BC)
    
    button_BF = QtGui.QPushButton("BodyForce")
    #ewh = elmer_window_handler.elmerWindowHandler()
    button_BF.clicked.connect(bodyforce)
    layout.addWidget(button_BF)
    
    button_boundary = QtGui.QPushButton("Boundary")
    #ewh = elmer_window_handler.elmerWindowHandler()
    button_boundary.clicked.connect(boundary)
    layout.addWidget(button_boundary)
    
    button_body = QtGui.QPushButton("Body")
    #ewh = elmer_window_handler.elmerWindowHandler()
    button_body.clicked.connect(body)
    layout.addWidget(button_body)

    button_initial = QtGui.QPushButton("Initial")
    #ewh = elmer_window_handler.elmerWindowHandler()
    button_initial.clicked.connect(initial)
    layout.addWidget(button_initial)

    button_sifwrite = QtGui.QPushButton("Write sif")
    button_sifwrite.clicked.connect(sif_write)
    layout.addWidget(button_sifwrite)

    window.setLayout(layout)    
    window.show()    
    
    # Run the main Qt loop
    app.exec_()

if __name__ == "__main__":
    start_GUI()


