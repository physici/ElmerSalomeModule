# -*- coding: utf-8 -*-
"""
Created on Sat Sep  3 14:35:56 2016

@author: Rainer Jacob

Salome Plugin-manager file for declaration of Elmer functionality to Salome
"""

from PyQt4 import QtGui

import salome_pluginsmanager as sp
import sys
import os

plugin_path = ""
# add SALOME_PLUGIN_PATH to Python environment for easier module import
if (os.environ.get("SALOME_PLUGINS_PATH") is not None):
    plugin_path = os.environ.get("SALOME_PLUGINS_PATH") +\
                  os.sep + "ElmerSalome"
if not (os.path.exists(plugin_path + os.sep + "elmer_window_handler.py")):
    import inspect
    plugin_path = os.path.dirname(inspect.getfile(inspect.currentframe())) +\
                  os.sep + "ElmerSalome"

sys.path.append(plugin_path)

if not (os.path.exists(plugin_path + os.sep + "elmer_window_handler.py")):
    sys.exit("No Elmer module found")

# import window handler
import elmer_window_handler as ewh

# global variable the will contain the Elmer-class and its memory-location
global main

# the environement variable is required to prevent the re-initialization
# of the Elmer-class each time the menu is opened, otherwise everything will
# be lost again, see http://www.salome-platform.org/forum/forum_12/575675631/639739196
if os.getenv("already_initialized", "0") != "1":
    main = ewh.elmerWindowHandler()

os.environ["already_initialized"] = "1"

# define about Function
def about(context):
    global main
    # get active module and check if SMESH
    active_module = context.sg.getActiveComponent()
    if active_module != "SMESH":
        QtGui.QMessageBox.about(None, str(active_module),
                                "Functionality is only provided in mesh module.")
        return

    title = "ELMER interface for SALOME editor"
    msg = "Interface that allows setup of an Elmer simulation with the help of the Salome Mesh editor and generation of necessary sif-file.\n"
    msg1 = "The mesh has to be exported as *.unv and converted with ELMER GRID. Simulation has to be started separately.\n\n"
    msg2 = "by raja, mzenker, 2017."
    QtGui.QMessageBox.about(None, title, msg + msg1 + msg2)
    return


# define generalSetup function
def generalSetup(context):
    global main
    # get active module and check if SMESH
    active_module = context.sg.getActiveComponent()
    if active_module != "SMESH":
        QtGui.QMessageBox.about(None, str(active_module),
                                "Functionality is only provided in mesh module.")
        return

    main.showGeneralSetup()


def showEquations(context):
    """Make a new equation set and call the dynamic editor"""
    global main
    # get active module and check if SMESH
    active_module = context.sg.getActiveComponent()
    if active_module != "SMESH":
        QtGui.QMessageBox.about(None, str(active_module),
                                "Functionality is only provided in mesh module.")
        return

    main.showAddEquation()


def showMaterials(context):
    """Make a new material set and call the dynamic editor"""
    global main
    # get active module and check if SMESH
    active_module = context.sg.getActiveComponent()
    if active_module != "SMESH":
        QtGui.QMessageBox.about(None, str(active_module),
                                "Functionality is only provided in mesh module.")
        return

    main.showAddMaterial()


def defineElementProperties(context):
    """Open dialog to set element properties"""
    global main, sp
    active_module = context.sg.getActiveComponent()
    if active_module != "SMESH":
        QtGui.QMessageBox.about(None, str(active_module),
                                "Functionality is only provided in mesh module.")
        return

    # check shape, should be solid/body
    selCount = sp.sg.SelectedCount()
    if selCount == 0:
        QtGui.QMessageBox.about(None, str(active_module),
                                "Nothing selected. Please select a volume/face or group of.")
        return
    else:
        objID = sp.sg.getSelected(0)
        salomeObj = sp.salome.myStudy.FindObjectID(objID)
        parentGroupCategory = salomeObj.GetFather().GetName()
        if "Volumes" in parentGroupCategory:
            main.showBodyPropertyDefinition(salomeObj.GetName())
            return
        if "Faces" in parentGroupCategory:
            main.showBoundaryPropertyDefinition(salomeObj.GetName())
            return
        else:
            mes = "Invalid selection. Check selection."
            QtGui.QMessageBox.about(None, str(active_module), mes)
            return


def showBodyForces(context):
    """Make a new body force set and call the dynamic editor"""
    global main, sp
    active_module = context.sg.getActiveComponent()
    if active_module != "SMESH":
        QtGui.QMessageBox.about(None, str(active_module),
                                "Functionality is only provided in mesh module.")
        return

    main.showAddBodyForce()

def showBoundaryConditions(context):
    """Make a new boundary condition set and call the dynamic editor"""
    global main, sp
    active_module = context.sg.getActiveComponent()
    if active_module != "SMESH":
        QtGui.QMessageBox.about(None, str(active_module),
                                "Functionality is only provided in mesh module.")
        return

    main.showAddBoundaryCondition()

def showInitialConditions(context):
    """Make a new initial condition set and call the dynamic editor"""
    global main, sp
    active_module = context.sg.getActiveComponent()
    if active_module != "SMESH":
        QtGui.QMessageBox.about(None, str(active_module),
                                "Functionality is only provided in mesh module.")
        return

    main.showAddInitialCondition()
    
def writeSif(context):
    main.sif_write()

# declare ShowWindow-Function to plugin manager
sp.AddFunction('ELMER/About', 'About ELMER plugin', about)
sp.AddFunction('ELMER/General settings', 'General simulation settings', generalSetup)
sp.AddFunction('ELMER/Equations', 'Equations', showEquations)
sp.AddFunction('ELMER/Materials', 'Materials', showMaterials)
sp.AddFunction('ELMER/Body forces', 'Body forces', showBodyForces)
sp.AddFunction('ELMER/Boundary conditions', 'Boundary conditions', showBoundaryConditions)
sp.AddFunction('ELMER/Initial conditions', 'Initial conditions', showInitialConditions)
sp.AddFunction('ELMER/Properties of selected element', 'Properties', defineElementProperties)
sp.AddFunction('ELMER/Write Solver Input File', 'Write sif', writeSif)
