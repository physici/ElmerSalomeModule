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
#add SALOME_PLUGIN_PATH to Python environment for easier module import
if (os.environ.get("SALOME_PLUGINS_PATH") != None):
    plugin_path =  os.environ.get("SALOME_PLUGINS_PATH") + "\\ElmerSalome"
else:
    import inspect
    plugin_path = os.path.dirname(inspect.getfile(inspect.currentframe()))  + "\\ElmerSalome"

sys.path.append(plugin_path)

if not (os.path.exists("{}\\elmer_window_handler.py".format(plugin_path))):
    sys.exit("No Elmer module found")

#import window handler
import elmer_window_handler as ewh

#required to keep reference to all created widgets, will be overwritten everytime
qwidget = QtGui.QWidget()

main = ewh.elmerWindowHandler()

#define about Function
def about(context):
    global main, qwidget
    #get active module and check if SMESH
    active_module = context.sg.getActiveComponent()
    if active_module != "SMESH":
        QtGui.QMessageBox.about(None, str(active_module),
                                    "Functionality is only provided in mesh module.")
        return
    return
    
#define generalSetup function
def generalSetup(context):
    global main, qwidget
    #get active module and check if SMESH
    active_module = context.sg.getActiveComponent()
    if active_module != "SMESH":
        QtGui.QMessageBox.about(None, str(active_module),
                                    "Functionality is only provided in mesh module.")
        return
    main.showGeneralSetup()
    
def showEquations(context):
    """Make a new equation sub-menu and call the dynamic editor"""
    global main, qwidget
     #get active module and check if SMESH
    active_module = context.sg.getActiveComponent()
    if active_module != "SMESH":
        QtGui.QMessageBox.about(None, str(active_module),
                                    "Functionality is only provided in mesh module.")
        return   
    
    main.showAddEquation()
    
def showMaterials(context):
    """Make a new material sub-menu and call the dynamic editor"""
    global main, qwidget
     #get active module and check if SMESH
    active_module = context.sg.getActiveComponent()
    if active_module != "SMESH":
        QtGui.QMessageBox.about(None, str(active_module),
                                    "Functionality is only provided in mesh module.")
        return   
    
    main.showAddMaterial()      
    
def defineBodyProperties(context):
    """Open dialog to set body properties"""
    global main, qwidget, sp
    active_module = context.sg.getActiveComponent()
    if active_module != "SMESH":
        QtGui.QMessageBox.about(None, str(active_module),
                                    "Functionality is only provided in mesh module.")
        return   
    
    #chech shape, should be solid/body
    objID = sp.sg.getSelected(0)
    salomeObj = sp.salome.myStudy.FindObjectID(objID)
    parentGroupCategory = salomeObj.GetFather().GetName()
    if "Volumes"  in parentGroupCategory:
        main.showBodyPropertyDefinition(salomeObj.GetName())
        return
    if "Faces" in parentGroupCategory:
        main.showBoundaryPropertyDefinition(salomeObj.GetName())
        return
    else:
        mes =  "Invalid selection. Check selection."
        QtGui.QMessageBox.about(None, str(active_module), mes)
        return      
    
    
    
#declare ShowWindow-Function to plugin manager
sp.AddFunction('ELMER/About', 'About ELMER plugin', about)
sp.AddFunction('ELMER/Equations', 'Equations', showEquations)
sp.AddFunction('ELMER/Materials', 'Materials', showMaterials)
#sp.AddFunction('ELMER/Properties of selected element', 'Properties', defineBodyProperties)