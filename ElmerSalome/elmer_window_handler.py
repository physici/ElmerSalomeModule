# -*- coding: utf-8 -*-
"""
Created on Sat Sep  3 14:31:15 2016

@author: Rainer Jacob
"""

from PyQt4 import QtGui
from PyQt4 import QtXml
from PyQt4 import QtCore

import os, os.path
import sys
import glob
import tempfile

from xml.etree import ElementTree as et

import solverparameters
import generalsetup
import dynamiceditor

path = os.path.dirname(os.path.abspath(__file__))
path_forms = path + "\\forms\\"
path_edfs = path + "\\edf\\"

class elmerWindowHandler():

    equationEditor = []
    materialEditor = []
    solverParameterEditor = []
    _elmerDefs = None
    _listview = None
    _window = None

       
    def __init__(self):
        self.xmlMerge(path_edfs) 
        self._parent = self

    def about(self):
        QtGui.QMessageBox.about(None, "About ELMER window handler",
                                        "Provides a handler to access ELMER configuration windows.\n" \
                                        "Requires ELMER, ELMERGUI and ELMER_HOME variable to be set.\n\n" \
                                        "Functionality provided only in Mesh-module.")
        
    def showGeneralSetup(self):
        """Initialize an instance of GeneralSetup and returns it to Salome"""
        ge = generalsetup.GeneralSetup(path_forms)
        return ge

    def showSolverParametersEditor(self):
        """Initialize an instance of Solver Param Editor and returns it to Salome"""
        sp = solverparameters.SovlerParameterEditor(path_forms)
        return sp
        
    def showAddEquation(self):
        """Creates a new instance of the dynamic editor for adding an equation"""
        
        #create a horizontal split layout
        window = QtGui.QWidget()
        layout = QtGui.QHBoxLayout()

        de = dynamiceditor.DynamicEditor()
        self.equationEditor.append(de)
        current = len(self.equationEditor) - 1
        de.setupTabs(self._elmerDefs, "Equation", current)
        
        de.applyButton.setText("Apply")
        de.discardButton.setText("Cancel")
    
        de.dynamicEditorReady[int, int].connect(self.pdeEditorFinishedSlot)    
        
        de.spareButton.setText("Edit Solver Settings")
        de.spareButton.show()
        de.dynamicEditorSpareButtonClicked[int, int].connect(self.editNumericalMethods)
        
        de.nameEdit.textChanged.connect(self.dynamicEditorNameChange)
                    
        #fill list view with items from material collection
        listview = QtGui.QListWidget()
        for equation in self.equationEditor:
            item = QtGui.QListWidgetItem()
            item.setText(equation.nameEdit.text())
            listview.addItem(item)
        listview.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Expanding)
            
        layout.addWidget(listview)
        layout.addWidget(de)
            
        window.setWindowTitle("Equation Editor")
        window.setLayout(layout)
        
        self._window = window
        self._listview = listview
        window.show()
        
        return window
        
    def showAddMaterial(self):
        """Creates a new instance of the dynamic editor for adding a material"""

        #create a horizontal split layout
        window = QtGui.QWidget()
        layout = QtGui.QHBoxLayout()
              
        de = dynamiceditor.DynamicEditor()
        self.materialEditor.append(de)
        current = len(self.materialEditor) - 1
        
        de.setupTabs(self._elmerDefs, "Material", current)
        de.applyButton.setText("Apply")
        de.discardButton.setText("Cancel")
          
        de.dynamicEditorReady[int, int].connect(self.matEditorFinishedSlot)

        #Use "spareButton" to invoke material library:
        de.spareButton.setText("Material library")
        de.spareButton.show()
        
        de.dynamicEditorSpareButtonClicked[int, int].connect(self.showMaterialLibrary)
        de.nameEdit.textChanged.connect(self.dynamicEditorNameChange)
          
        #fill list view with items from material collection
        listview = QtGui.QListWidget()
        for mat in self.materialEditor:
            item = QtGui.QListWidgetItem()
            item.setText(mat.nameEdit.text())
            listview.addItem(item)
        listview.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Expanding)
            
        layout.addWidget(listview)
        layout.addWidget(de)
            
        window.setWindowTitle("Equation Editor")
        window.setLayout(layout)
        
        self._window = window
        self._listview = listview
        window.show()
        
        return window
    
    def matEditorFinishedSlot(self, signal, ids):
        """Method for handling the button events in the solver settings\n
        signal = the button hit\n
        ids = ID of the equation set"""

        return      
        
    def showMaterialLibrary(self, signal, ids):
        """Method for handling the button events in the solver settings\n
        signal = the button hit\n
        ids = ID of the equation set"""

        return  

        
    def pdeEditorFinishedSlot(self, signal, ids):
        """Method for handling the button events in the solver settings\n
        signal = the button hit\n
        ids = ID of the equation set"""
        listview = self._listview
        item = listview.item(ids)
        de = self.equationEditor[ids]
        equationName = str(de.nameEdit.text()).strip()
        
        signalOK = False
        if(signal == dynamiceditor.MatTypes.MAT_OK or
            signal == dynamiceditor.MatTypes.MAT_APPLY):
            signalOK = True

        if(signalOK and not equationName):
            sys.stdout.write("No equation name\n")
            sys.stdout.flush()
            return
        
        if(signalOK):
            """ToDo"""
            item.setText(equationName)
            if signal == dynamiceditor.MatTypes.MAT_OK:
                self._window.close()
                    
        elif(signal == dynamiceditor.MatTypes.MAT_NEW):
            """ToDo"""          
            ewh = elmerWindowHandler()
            de = ewh.showAddEquation()
            self._window.close()
        
        elif(signal == dynamiceditor.MatTypes.MAT_DELETE):
            """ToDo"""
            del self.equationEditor[ids]
            self._window.close()
            
    def editNumericalMethods(self, current, ids):
        """Edit the solver specific properties\n
        current = ID of the equation set that should be edited"""

        title = ""
        for i in range(0, len(self.equationEditor)):
            title = self.equationEditor[i].tabWidget.tabText(current)
            break
        
        if(title == "General"):
            sys.stdout.write("No solver controls for 'General' equation options")
            sys.stdout.flush()
            return
            
        if(current >= len(self.solverParameterEditor)):
            self.solverParameterEditor.append(solverparameters.SovlerParameterEditor(path_forms))

        spe = self.solverParameterEditor[current]
        spe.setWindowTitle("Solver control for {}".format(title))
        spe.solverName = title
        
        if(spe.generalOptions == None):
            spe.generalOptions = dynamiceditor.DynamicEditor()
            spe.generalOptions.setupTabs(self._elmerDefs, "Solver", current)
            spe.solverControlTabs.insertTab(0, spe.generalOptions.tabWidget.widget(current),
                                            "Solver specific options")
        
        for i in range(0, spe.generalOptions.tabWidget.count()):
            if(spe.generalOptions.tabWidget.tabText(i) == title):
                spe.solverControlTabs.insertTab(0, spe.generalOptions.tabWidget.widget(i),
                                            "Solver specific options")       
                break
        
        spe.show()
            
          
    def dynamicEditorNameChange(self, t):
        """ToDo"""
        return
               
    def xmlMerge(self, path):
        """Merges all edf-xml files in the given directory into a temporary file\n
        returns the temporary file object with the cursor at the beginning"""
        
        mybuf = tempfile.TemporaryFile()
    
        gen_file = path + "edf.xml"
        
        first = et.parse(gen_file).getroot()    
        
        xml_files = glob.glob(path + "*.xml")
        xml_files = [file for file in xml_files if not os.path.basename(file).startswith("edf")]
    
        for xml_file in xml_files:
            data = et.parse(xml_file).getroot()
            first.extend(data)
        
        mybuf.write(et.tostring(first))
        mybuf.seek(0)
        temp = mybuf.read().decode()
        mybuf.close()
        
        self._elmerDefs = QtXml.QDomDocument()    
        self._elmerDefs.setContent(temp)        
        print("Fertig")

if __name__ == "__main__":
    path = os.path.dirname(os.path.abspath(__file__))
    path_forms = path + "\\forms\\"
    path_edfs = path + "\\edf\\"
    sys.path.append(r"C:\opt\SALOME-7.8.0-WIN64\PLUGINS\ElmerSalome")
    app = QtGui.QApplication(sys.argv)
    ewh = elmerWindowHandler()
    de = ewh.showAddEquation()
    #sp = ewh.showSolverParametersEditor()
    #sp.show()
    sys.exit(app.exec_())


