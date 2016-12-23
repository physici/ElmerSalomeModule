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
import bodypropertyeditor
import boundarypropertyeditor

path = os.path.dirname(os.path.abspath(__file__))
path_forms = path + os.sep + "forms" + os.sep
path_edfs = path + os.sep + "edf" + os.sep

main = None

class elmerWindowHandler():

    _equationEditor = []
    _materialEditor = []
    _solverParameterEditor = []
    _bodyForceEditor = []
    _initialConditionEditor = []
    _boundaryConditionEditor = []
    _elementProperties = {}
    _elmerDefs = None
    _listview = None
    _window = None
    _eqWindow = None
    _matWindow = None
    _matCurrent = 0
    _eqCurrent = 0

       
    def __init__(self):
        self._xmlMerge(path_edfs) 
        self._parent = self

    def about(self):
        QtGui.QMessageBox.about(None, "About ELMER window handler",
                                        "Provides a handler to access ELMER configuration windows.\n" \
                                        "Requires ELMER, ELMERGUI and ELMER_HOME variable to be set.\n\n" \
                                        "Functionality provided only in Mesh-module.")

    def showBoundaryPropertyDefinition(self, objName):
        """Dialog to define geometry properties\n
        name = name of the element as provided in Salome Object Browser"""

        be = boundarypropertyeditor.BoundaryPropertyEditor(path_forms)
        be.objName = objName
        be.setWindowTitle("Boundary property for boundary {}".format(objName)) 
        
        #populate comboboxes
        count = 1
        be.boundaryConditionCombo.addItem("", "Empty")
        count += 1
        for element in self._boundaryConditionEditor:
            name = str(element.nameEdit.text()).strip()
            be.boundaryConditionCombo.addItem(name, name)
            count += 1
        count = 1

        # check if element has properties already
        if objName in self._elementProperties:        
            properties = self._elementProperties[objName]
            be.boundaryConditionCombo.setCurrentIndex(be.boundaryConditionCombo.findText(properties.boundaryProperties))
            be.boundaryAsABody.setCheckState(properties.bodyCondition)

            
        #connect to slot
        be.boundaryPropertyEditorApply.connect(self._boundaryPropertyChanged)
            
        be.show()
        self._window = be
        return self._window

        
    def showBodyPropertyDefinition(self, objName):
        """Dialog to define geometry properties\n
        name = name of the element as provided in Salome Object Browser"""

        be = bodypropertyeditor.BodyPropertyEditor(path_forms)
        be.nameEdit.setText(objName)        
        be.setWindowTitle("Body property for body {}".format(objName)) 
        
        #populate comboboxes
        count = 1
        be.equationCombo.addItem("", "Empty")
        count += 1
        for element in self._equationEditor:
            name = str(element.nameEdit.text()).strip()
            be.equationCombo.addItem(name, name)
            count += 1
        count = 1
        be.materialCombo.addItem("", "Empty")
        count += 1
        for element in self._materialEditor:
            name = str(element.nameEdit.text()).strip()
            be.materialCombo.addItem(name, name)
            count += 1
        count = 1
        be.bodyForceCombo.addItem("", "Empty")
        count += 1
        for element in self._bodyForceEditor:
            name = str(element.nameEdit.text()).strip()
            be.bodyForceCombo.addItem(name, name)
            count += 1
        count = 1
        be.initialConditionCombo.addItem("", "Empty")
        count += 1
        for element in self._initialConditionEditor:
            name = str(element.nameEdit.text()).strip()
            be.initialConditionCombo.addItem(name, name)
            count += 1

        # check if element has properties already
        if objName in self._elementProperties:        
            properties = self._elementProperties[objName]
            be.equationCombo.setCurrentIndex(be.equationCombo.findText(properties.equation))
            be.materialCombo.setCurrentIndex(be.materialCombo.findText(properties.material))
            be.bodyForceCombo.setCurrentIndex(be.bodyForceCombo.findText(properties.force))
            be.initialConditionCombo.setCurrentIndex(be.initialConditionCombo.findText(properties.initial))
            
        #connect to slot
        be.bodyPropertyEditorApply.connect(self._bodyPropertyChanged)
            
        be.show()
        self._window = be
        return self._window
        
    def showGeneralSetup(self):
        """Initialize an instance of GeneralSetup and returns it to Salome"""
        ge = generalsetup.GeneralSetup(path_forms)
        return ge

    def showSolverParametersEditor(self):
        """Initialize an instance of Solver Param Editor and returns it to Salome"""
        sp = solverparameters.SolverParameterEditor(path_forms)
        return sp
        
    def showAddEquation(self):
        """Creates a new instance of the dynamic editor for adding an equation"""
        
        #create a horizontal split layout
        if not self._eqWindow:
            self._eqWindow = QtGui.QWidget()
            layout = QtGui.QHBoxLayout()
            self._listview = QtGui.QListWidget()
            self._listview.clicked[QtCore.QModelIndex].connect(self._eqitemchanged)
            layout.addWidget(self._listview)               
            self._eqWindow.setLayout(layout)

            self._pdeEditorFinishedSlot(dynamiceditor.MatTypes.MAT_NEW, 0)
            
            self._eqWindow.show()
        else:
            self._eqWindow.show()

        return self._eqWindow
        
    def showAddMaterial(self):
        """Creates a new instance of the dynamic editor for adding a material"""

        if not self._matWindow:
            #create a horizontal split layout
            self._matWindow = QtGui.QWidget()
            layout = QtGui.QHBoxLayout()
            self._listview = QtGui.QListWidget()
            self._listview.clicked[QtCore.QModelIndex].connect(self._matitemchanged)            
            layout.addWidget(self._listview)          
            self._matWindow.setWindowTitle("Material Library")
            self._matWindow.setLayout(layout)
            
            #check if there are already some materials
            if len(self._materialEditor) == 0:
                self._matEditorFinishedSlot(dynamiceditor.MatTypes.MAT_NEW, 0)
            else:
                #populate list and reset signal slot
                for mat in self._materialEditor:
                    item = QtGui.QListWidgetItem()
                    item.setText(mat.nameEdit.text())
                    self._listview.addItem(item)
                    mat.dynamicEditorReady.disconnect()
                    mat.dynamicEditorReady[int, int].connect(self._matEditorFinishedSlot) 
                #show first material
                de = self._materialEditor[0]
                layout.insertWidget(1, de)
                self._matWindow.setWindowTitle(de.nameEdit.text())
                de.show()           
            self._matWindow.show()
        else:
            self._matWindow.show()
        
        return self._matWindow

    def _boundaryPropertyChanged(self, boundaryPropertyEditor, name):
        """Signal when body properties have changed"""
        self._elementProperties.update({str(name): boundaryPropertyEditor})

        
    def _bodyPropertyChanged(self, bodyPropertyEditor, name):
        """Signal when body properties have changed"""
        self._elementProperties.update({str(name): bodyPropertyEditor})
       

    def _eqitemchanged(self, index):
        """Method for changing the selected item in the equation editor view"""

        # delete second item == editor
        layout = self._eqWindow.layout()
        item = layout.takeAt(1)
        if item:
            item.widget().close()
        # insert the selected editor
        de = self._equationEditor[index.row()]
        de.show()
        layout.insertWidget(1, de)
        
        self._eqWindow.setWindowTitle(de.nameEdit.text())     
  
        
    def _matitemchanged(self, index):
        """Method for changing the selected item in the equation editor view"""
         # delete second item == editor
        layout = self._matWindow.layout()
        item = layout.takeAt(1)
        item.widget().close()
        # insert the selected editor
        de = self._materialEditor[index.row()]
        layout.insertWidget(1, de)
        de.show()
        self._matWindow.setWindowTitle(de.nameEdit.text())     
        
        
    def _matEditorFinishedSlot(self, signal, ids):
        """Method for handling the button events in the solver settings\n
        signal = the button hit\n
        ids = ID of the equation set"""
        for mat in self._materialEditor:
            temp = mat.ID
            if temp == ids:
                ids = self._materialEditor.index(mat)
                break        
            
        listview = self._listview
        
        signalOK = False
        if(signal == dynamiceditor.MatTypes.MAT_OK or
            signal == dynamiceditor.MatTypes.MAT_APPLY):
            signalOK = True

        if(signalOK):
            """ToDo"""
            item = listview.item(ids)
            de = self._materialEditor[ids]
            matName = str(de.nameEdit.text()).strip()
            if not matName:
                sys.stdout.write("Material Name\n")
                sys.stdout.flush()
                return
            else:
                item.setText(matName)
                self._matWindow.setWindowTitle(matName)
                if signal == dynamiceditor.MatTypes.MAT_OK:
                    self._matWindow.hide()
                    
        elif(signal == dynamiceditor.MatTypes.MAT_NEW):
            """Create a new material"""          
            # get window and layout
            window = self._matWindow
            layout = window.layout()
            
            # new instance of the dynamic editor
            current = self._matCurrent 
            de = dynamiceditor.DynamicEditor()
            self._materialEditor.append(de)
            de.setupTabs(self._elmerDefs, "Material", current)
            de.applyButton.setText("Apply")
            de.discardButton.setText("Delete")
            de.dynamicEditorReady[int, int].connect(self._matEditorFinishedSlot)    
            de.spareButton.setText("Show Material Library")
            de.spareButton.show()
            de.dynamicEditorSpareButtonClicked[int, int].connect(self._showMaterialLibrary)
                     
            #clear right side of layout and at the new dynamic editor
            item = layout.takeAt(1)
            if item is not None:
                item.widget().close()                
            layout.addWidget(de)

            #add item to list
            item = QtGui.QListWidgetItem()
            item.setText(de.nameEdit.text())
            self._listview.addItem(item)     
            self._matWindow.setWindowTitle(de.nameEdit.text()) 
            
            #set new as selected
            count = len(self._materialEditor)
            self._listview.item(count - 1).setSelected(True)
            
            self._matCurrent += 1

        
        elif(signal == dynamiceditor.MatTypes.MAT_DELETE):
            """Remove the current material editor from the collection"""
            if len(self._materialEditor) > 1:
                #remove the current equation                
                item = self._listview.takeItem(ids)
                del self._materialEditor[ids]
                #show the previous equation
                if ids > 1:
                    ids -= 1
                self._listview.item(ids).setSelected(True)                  
                layout = self._matWindow.layout()
                item = layout.takeAt(1)
                item.widget().close()
                de = self._materialEditor[ids]
                layout.insertWidget(1, de)
                de.show()
                self._matWindow.setWindowTitle(de.nameEdit.text())
            else:
                #remove the current equation                
                del self._materialEditor[ids]
                self._materialEditor = []
                self._matWindow.hide()        
       
    def _showMaterialLibrary(self, current, ids):
        return
        
    def _pdeEditorFinishedSlot(self, signal, ids):
        """Method for handling the button events in the solver settings\n
        signal = the button hit\n
        ids = ID of the equation set"""

        for eq in self._equationEditor:
            temp = eq.ID
            if temp == ids:
                ids = self._equationEditor.index(eq)
                break        
        
        listview = self._listview     
        signalOK = False
        if(signal == dynamiceditor.MatTypes.MAT_OK or
            signal == dynamiceditor.MatTypes.MAT_APPLY):
            signalOK = True

        if(signalOK):
            """ToDo"""
            item = listview.item(ids)
            de = self._equationEditor[ids]
            equationName = str(de.nameEdit.text()).strip()
            if not equationName:
                sys.stdout.write("No equation name\n")
                sys.stdout.flush()
                return
            else:
                item.setText(equationName)
                self._eqWindow.setWindowTitle(equationName)
                if signal == dynamiceditor.MatTypes.MAT_OK:
                    self._eqWindow.hide()
                    
        elif(signal == dynamiceditor.MatTypes.MAT_NEW):
            """Create a new material"""          
            # get window and layout
            window = self._eqWindow
            layout = window.layout()
            
            # new instance of the dynamic editor
            current = self._eqCurrent
            de = dynamiceditor.DynamicEditor()
            self._equationEditor.append(de)
            de.setupTabs(self._elmerDefs, "Equation", current)
            de.applyButton.setText("Apply")
            de.discardButton.setText("Delete")
            de.dynamicEditorReady[int, int].connect(self._pdeEditorFinishedSlot)    
            de.spareButton.setText("Edit Solver Settings")
            de.spareButton.show()
            de.dynamicEditorSpareButtonClicked[int, int].connect(self._editNumericalMethods)
                     
            #clear right side of layout and at the new dynamic editor
            item = layout.takeAt(1)
            if item is not None:
                item.widget().close()                
            layout.addWidget(de)

            #add item to list
            item = QtGui.QListWidgetItem()
            item.setText(de.nameEdit.text())
            self._listview.addItem(item)    
            #set new as selected
            count = len(self._equationEditor)
            self._listview.item(count - 1).setSelected(True)
            
            self._eqWindow.setWindowTitle(de.nameEdit.text())    
            
            self._eqCurrent += 1

        
        elif(signal == dynamiceditor.MatTypes.MAT_DELETE):
            """Remove the current equation editor from the collection"""
            if len(self._equationEditor) > 1:
                #remove the current equation                
                item = self._listview.takeItem(ids)
                del self._equationEditor[ids]
                #show the previous equation
                if ids > 0:
                    ids -= 1
                self._listview.item(ids).setSelected(True)                  
                layout = self._eqWindow.layout()
                item = layout.takeAt(1)
                item.widget().close()
                de = self._equationEditor[ids]
                layout.insertWidget(1, de)
                de.show()
                self._eqWindow.setWindowTitle(de.nameEdit.text())
            else:
                #remove the current equation                
                del self._equationEditor[ids]
                self._equationEditor = []
                self._eqWindow.hide()                       

            
    def _editNumericalMethods(self, current, ids):
        """Edit the solver specific properties\n
        current = ID of the equation set that should be edited"""

        title = ""
        for i in range(0, len(self._equationEditor)):
            title = self._equationEditor[i].tabWidget.tabText(current)
            break
        
        if(title == "General"):
            sys.stdout.write("No solver controls for 'General' equation options")
            sys.stdout.flush()
            return
            
        if(current >= len(self._solverParameterEditor)):
            self._solverParameterEditor.append(solverparameters.SolverParameterEditor(path_forms))

        spe = self._solverParameterEditor[current]
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
                           
    def _xmlMerge(self, path):
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
        #print("Fertig")

if __name__ == "__main__":
    path = os.path.dirname(os.path.abspath(__file__))
    path_forms = path + os.sep + "forms" +  os.sep
    path_edfs = path + os.sep + "edf" + os.sep
    sys.path.append(r"C:\opt\SALOME-7.8.0-WIN64\PLUGINS\ElmerSalome")
    app = QtGui.QApplication(sys.argv)
    ewh = elmerWindowHandler()
    sp = ewh.showAddEquation()    
    #sp = ewh.showSolverParametersEditor()
    #sp.show()
    sys.exit(app.exec_())