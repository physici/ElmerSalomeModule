# -*- coding: utf-8 -*-
"""
Created on Sat Sep  3 14:35:56 2016

@author: Rainer Jacob

Salome Plugin-manager file for declaration of Elmer functionality to Salome
"""

try:
    from PyQt4 import QtGui
except ImportError:
    from PyQt5 import QtWidgets as QtGui

import salome_pluginsmanager as sp
import smesh
import salome
import sys
import os
import subprocess
import pdb

# %% setup
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
# be lost again,
# see http://www.salome-platform.org/forum/forum_12/575675631/639739196
if os.getenv("already_initialized", "0") != "1":
    main = ewh.ElmerWindowHandler()

os.environ["already_initialized"] = "1"


# %% define about Function
def about(context):
    """Shows an info dialog for the plugin. May contain additional information
    in the future.

    Args:
    -----
    context: salome context
        Context variable provided by the Salome environment
    """

    global main, QtGui
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


# %% generalSetup
def generalSetup(context):
    """Shows the general setup dialog for Elmer.

    Args:
    -----
    context: salome context
        Context variable provided by the Salome environment
    """
    global main, QtGui
    # get active module and check if SMESH
    active_module = context.sg.getActiveComponent()
    if active_module != "SMESH":
        QtGui.QMessageBox.about(None, str(active_module),
                                "Functionality is only provided in mesh module.")
        return

    main.showGeneralSetup()


# %% equation definition
def showEquations(context):
    """Shows the window for the definition of equations.

    Args:
    -----
    context: salome context
        Context variable provided by the Salome environment
    """
    global main, QtGui
    # get active module and check if SMESH
    active_module = context.sg.getActiveComponent()
    if active_module != "SMESH":
        QtGui.QMessageBox.about(None, str(active_module),
                                "Functionality is only provided in mesh module.")
        return

    main.showAddEquation()


# %% material defintion
def showMaterials(context):
    """Shows the window for the definition of materials.

    Args:
    -----
    context: salome context
        Context variable provided by the Salome environment
    """
    global main, QtGui
    # get active module and check if SMESH
    active_module = context.sg.getActiveComponent()
    if active_module != "SMESH":
        QtGui.QMessageBox.information(None, str(active_module),
                                "Functionality is only provided in mesh module.")
        return

    main.showAddMaterial()


# %% element properties
def defineElementProperties(context):
    """Context sensitive window for setting the element properties. Faces and
    bodies will create different windows.

    Args:
    -----
    context: salome context
        Context variable provided by the Salome environment
    """
    global main, sp, QtGui
    # get active module and check if SMESH
    active_module = context.sg.getActiveComponent()
    if active_module != "SMESH":
        QtGui.QMessageBox.information(None, str(active_module),
                                "Functionality is only provided in mesh module.")
        return

    # get selection
    selCount = sp.sg.SelectedCount()
    if selCount == 0:
        QtGui.QMessageBox.information(None, str(active_module),
                                "Nothing selected. Please select a volume/face or group of.")
        return
    # check shape, should be volume or face
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
            QtGui.QMessageBox.warning(None, str(active_module), mes)
            return


# %% body forces
def showBodyForces(context):
    """Shows the window for the definition of body forces.

    Args:
    -----
    context: salome context
        Context variable provided by the Salome environment
    """
    global main, sp, QtGui
    # get active module and check if SMESH
    active_module = context.sg.getActiveComponent()
    if active_module != "SMESH":
        QtGui.QMessageBox.information(None, str(active_module),
                                "Functionality is only provided in mesh module.")
        return

    main.showAddBodyForce()


# %% boundary conditions
def showBoundaryConditions(context):
    """Shows the window for the definition of boundary conditions.

    Args:
    -----
    context: salome context
        Context variable provided by the Salome environment
    """
    global main, sp, QtGui
    # get active module and check if SMESH
    active_module = context.sg.getActiveComponent()
    if active_module != "SMESH":
        QtGui.QMessageBox.information(None, str(active_module),
                                "Functionality is only provided in mesh module.")
        return

    main.showAddBoundaryCondition()


# %% initial conditions
def showInitialConditions(context):
    """Shows the window for the definition of initial conditions.

    Args:
    -----
    context: salome context
        Context variable provided by the Salome environment
    """
    global main, sp, QtGui
    # get active module and check if SMESH
    active_module = context.sg.getActiveComponent()
    if active_module != "SMESH":
        QtGui.QMessageBox.information(None, str(active_module),
                                "Functionality is only provided in mesh module.")
        return

    main.showAddInitialCondition()


# %% mesh creation
def createMesh(context):
    """Context sensitive window for setting for mesh export. Only a mesh-node
    in the object tree of salome will create the correct output - unv-mesh and
    ElmerGrid mesh.

    Args:
    -----
    context: salome context
        Context variable provided by the Salome environment
    """
    global main, sp, smesh, salome, subprocess, QtGui, pdb
    # get active module and check if SMESH
    active_module = context.sg.getActiveComponent()
    if active_module != "SMESH":
        QtGui.QMessageBox.information(None, str(active_module),
                                "Functionality is only provided in mesh module.")
        return

    # get selection
    selCount = sp.sg.SelectedCount()
    if selCount == 0:
        QtGui.QMessageBox.warning(None, str(active_module),
                                  "Nothing selected. Please select a mesh.")
        return
    # check if selection == mesh
    else:
        objID = sp.sg.getSelected(0)
        ref = salome.IDToObject(objID)
        try:
            myMesh = smesh.Mesh(ref)
        except AttributeError:
            QtGui.QMessageBox.warning(None, str(active_module),
                                      "Selection is not a mesh.")
            return
        # get a filename for saving the unv-mesh
        title = 'Export mesh to file'
        fname = QtGui.QFileDialog.getSaveFileName(parent=None, caption=title,
                                                  filter='Mesh files (*.unv)')
        
        # Salome 8.2 behavior
        if isinstance(fname, tuple):
            fname = fname[0]
        
        # pdb.set_trace()
        # call to ElmerGrid for converting the unv-file to Elmer-readable file
        if fname:
            fname = os.path.normpath(str(fname))
            path = os.path.dirname(fname)
            # Linux does not add file ending automatically
            if not fname.endswith('.unv'):
                fname = '{}.unv'.format(fname)
            if os.path.exists(fname):
                os.remove(fname)
            myMesh.ExportUNV(fname)
            try:
                subprocess.Popen("ELMERGRID 8 2 {0} -autoclean -out {1}".format(fname, path))
            except OSError:
                QtGui.QMessageBox.about(None, "File IO error", "fname: {}, path: {}".format(fname, path))
                print fname
                print path
                return
            main.meshDirectory = path


# %% sif generator
def writeSif(context):
    """Calls the sif generator.

    Args:
    -----
    context: salome context
        Context variable provided by the Salome environment
    """
    global main, QtGui
    # get active module and check if SMESH
    active_module = context.sg.getActiveComponent()
    if active_module != "SMESH":
        QtGui.QMessageBox.information(None, str(active_module),
                                "Functionality is only provided in mesh module.")
        return

    main.sif_write()

# %% declare Elmer-Functions to plugin manager
sp.AddFunction('ELMER/About', 'About ELMER plugin', about)
sp.AddFunction('ELMER/General settings', 'General simulation settings', generalSetup)
sp.AddFunction('ELMER/Equations', 'Equations', showEquations)
sp.AddFunction('ELMER/Materials', 'Materials', showMaterials)
sp.AddFunction('ELMER/Body forces', 'Body forces', showBodyForces)
sp.AddFunction('ELMER/Boundary conditions', 'Boundary conditions', showBoundaryConditions)
sp.AddFunction('ELMER/Initial conditions', 'Initial conditions', showInitialConditions)
sp.AddFunction('ELMER/Properties of selected element', 'Properties', defineElementProperties)
sp.AddFunction('ELMER/Create mesh', 'Mesh creation', createMesh)
sp.AddFunction('ELMER/Write Solver Input File', 'Write sif', writeSif)
