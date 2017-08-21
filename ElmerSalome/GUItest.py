import sys
from PyQt4 import QtGui
from PyQt4 import QtXml
from PyQt4 import QtCore

sys.dont_write_bytecode = True

import elmer_window_handler
import sifwrite
import runsolver

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

def parallel():
    global sp
    sp = ewh.showParallelSettings()  

def sif_write():
    print('sifwrite test')
    ewh.sif_write()

def sif_read():
    ewh.sif_read()

def start_solver():
    print('start ElmerSolver...')
    ewh.start_Solver()

def start_GUI():
    global ewh
    # Create the Qt Application
    app = QtGui.QApplication(sys.argv)
    window = QtGui.QWidget()
    layout = QtGui.QVBoxLayout()

    ewh = elmer_window_handler.ElmerWindowHandler()

    ewh._initGeneralSetup()

    # Create buttons, connect and show them

    button_about = QtGui.QPushButton("About")
    button_about.clicked.connect(about)
    layout.addWidget(button_about)

    button_sifread = QtGui.QPushButton("Read sif")
    button_sifread.clicked.connect(sif_read)
    layout.addWidget(button_sifread)

    button_general = QtGui.QPushButton("General")
    button_general.clicked.connect(general)
    layout.addWidget(button_general)

    button_equation = QtGui.QPushButton("Equation")
    button_equation.clicked.connect(equation)
    layout.addWidget(button_equation)
    
    button_material = QtGui.QPushButton("Material")
    button_material.clicked.connect(material)
    layout.addWidget(button_material)
    
    button_BC = QtGui.QPushButton("BoundaryCondition")
    button_BC.clicked.connect(boundarycondition)
    layout.addWidget(button_BC)
    
    button_BF = QtGui.QPushButton("BodyForce")
    button_BF.clicked.connect(bodyforce)
    layout.addWidget(button_BF)
    
    button_boundary = QtGui.QPushButton("Boundary")
    button_boundary.clicked.connect(boundary)
    layout.addWidget(button_boundary)
    
    button_body = QtGui.QPushButton("Body")
    button_body.clicked.connect(body)
    layout.addWidget(button_body)

    button_initial = QtGui.QPushButton("Initial")
    button_initial.clicked.connect(initial)
    layout.addWidget(button_initial)

    button_sifwrite = QtGui.QPushButton("Write sif")
    button_sifwrite.clicked.connect(sif_write)
    layout.addWidget(button_sifwrite)

    button_parallelSettings = QtGui.QPushButton("Parallel Settings")
    button_parallelSettings.clicked.connect(parallel)
    layout.addWidget(button_parallelSettings)

    button_startsolver = QtGui.QPushButton("start ElmerSolver")
    button_startsolver.clicked.connect(start_solver)
    layout.addWidget(button_startsolver)

    window.setLayout(layout)    
    window.show()    
    
    # Run the main Qt loop
    app.exec_()

if __name__ == "__main__":
    start_GUI()


