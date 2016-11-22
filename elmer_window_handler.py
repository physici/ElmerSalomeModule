# -*- coding: utf-8 -*-
"""
Created on Sat Sep  3 14:31:15 2016

@author: Rainer Jacob
"""

import os
import os.path
import sys
import glob
import tempfile

from xml.etree import ElementTree as et

from PyQt4 import QtGui
from PyQt4 import QtXml
from PyQt4 import QtCore

import solverparameters
import generalsetup
import dynamiceditor
import bodypropertyeditor

path = os.path.dirname(os.path.abspath(__file__))
path_forms = path + "\\forms\\"
path_edfs = path + "\\edf\\"

main = None


class elmerWindowHandler():
    """Class for the main application handling all the windows and keeping
    track of all data"""

    # private fields
    _equationEditor = []
    _materialEditor = []
    _solverParameterEditor = []
    _bodyForceEditor = []
    _initialConditionEditor = []
    _boundaryConditionEditor = []
    _boundaryPropertyEditor = []
    _elementProperties = {}
    _elmerDefs = None
    _listview = None
    _window = None

    def __init__(self):
        """Constructor"""
        # create xml data from edf-files
        self._xmlMerge(path_edfs)
        self._parent = self

    def about(self):
        """Information display about class"""

        message = "Provides a handler to access ELMER configuration windows.\n" \
                  "Requires ELMER, ELMERGUI and ELMER_HOME variable to be set.\n\n" \
                  "Functionality provided only in Mesh-module."
        QtGui.QMessageBox.about(None, "About ELMER window handler", message)

    def showBodyPropertyDefinition(self, objName):
        """Dialog to define geometry properties\n
        name = name of the element as provided in Salome Object Browser"""

        be = bodypropertyeditor.BodyPropertyEditor(path_forms)
        be.nameEdit.setText(objName)
        be.setWindowTitle("Body property for body {}".format(objName))

        # populate comboboxes
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
        for element in self._materialEditor:
            name = str(element.nameEdit.text()).strip()
            be.bodyForceCombo.addItem(name, name)
            count += 1
        count = 1
        be.initialConditionCombo.addItem("", "Empty")
        count += 1
        for element in self._materialEditor:
            name = str(element.nameEdit.text()).strip()
            be.initialConditionCombo.addItem(name, name)
            count += 1

        # check if element has properties already
        if objName in self._elementProperties:
            properties = self._elementProperties[objName]
            be.equationCombo.setCurrentIndex(be.equationCombo.findData(properties.equation))
            be.materialCombo.setCurrentIndex(be.materialCombo.findData(properties.material))
            be.bodyForceCombo.setCurrentIndex(be.bodyForceCombo.findData(properties.force))
            be.initialConditionCombo.setCurrentIndex(be.initialConditionCombo.findData(properties.initial))

        # connect to slot
        be.bodyPropertyEditorApply.connect(self._bodyPropertyChanged)

        be.show()
        self._window = be
        return self._window

    def showGeneralSetup(self):
        """Initialize an instance of GeneralSetup and returns it to Salome"""

        ge = generalsetup.GeneralSetup(path_forms)
        return ge

    def showSolverParametersEditor(self):
        """Initialize an instance of Solver Param Editor
        and returns it to Salome"""
        sp = solverparameters.SovlerParameterEditor(path_forms)
        return sp

    def showAddEquation(self):
        """Creates a new instance of the dynamic editor
        for adding an equation"""

        # create a horizontal split layout
        self._window = QtGui.QWidget()
        layout = QtGui.QHBoxLayout()
        self._listview = QtGui.QListWidget()
        self._listview.clicked[QtCore.QModelIndex].connect(self._eqitemchanged)
        layout.addWidget(self._listview)
        self._window.setLayout(layout)

        # check if there are already some equations
        if len(self._equationEditor) == 0:
            self._pdeEditorFinishedSlot(dynamiceditor.MatTypes.MAT_NEW, 0)
        else:
            # populate list and reset signal slot
            for equation in self._equationEditor:
                item = QtGui.QListWidgetItem()
                item.setText(equation.nameEdit.text())
                self._listview.addItem(item)
                equation.dynamicEditorReady.disconnect()
                equation.dynamicEditorReady[int, int].connect(self._pdeEditorFinishedSlot)
            # show first item
            de = self._equationEditor[0]
            layout.insertWidget(1, de)
            self._window.setWindowTitle(de.nameEdit.text())
            de.show()
        self._window.show()

        return self._window

    def showAddMaterial(self):
        """Creates a new instance of the dynamic editor
        for adding a material"""

        # create a horizontal split layout
        self._window = QtGui.QWidget()
        layout = QtGui.QHBoxLayout()
        self._listview = QtGui.QListWidget()
        self._listview.clicked[QtCore.QModelIndex].connect(self._matitemchanged)
        layout.addWidget(self._listview)
        self._window.setWindowTitle("Material Library")
        self._window.setLayout(layout)

        # check if there are already some materials
        if len(self._materialEditor) == 0:
            self._matEditorFinishedSlot(dynamiceditor.MatTypes.MAT_NEW, 0)
        else:
            # populate list and reset signal slot
            for mat in self._materialEditor:
                item = QtGui.QListWidgetItem()
                item.setText(mat.nameEdit.text())
                self._listview.addItem(item)
                mat.dynamicEditorReady.disconnect()
                mat.dynamicEditorReady[int, int].connect(self._matEditorFinishedSlot)
            # show first material
            de = self._materialEditor[0]
            layout.insertWidget(1, de)
            self._window.setWindowTitle(de.nameEdit.text())
            de.show()
        self._window.show()

        return self._window

    def _bodyPropertyChanged(self, bodyPropertyEditor, name):
        """Signal when body properties have changed"""

        self._elementProperties.update({str(name): bodyPropertyEditor})

    def _eqitemchanged(self, index):
        """Method for changing the selected item in the equation editor view"""

        # delete second item == editor
        layout = self._window.layout()
        item = layout.takeAt(1)
        if item:
            item.widget().close()
        # insert the selected editor
        de = self._equationEditor[index.row()]
        layout.insertWidget(1, de)
        de.show()
        self._window.setWindowTitle(de.nameEdit.text())

    def _matitemchanged(self, index):
        """Method for changing the selected item in the equation editor view"""

        # delete second item == editor
        layout = self._window.layout()
        item = layout.takeAt(1)
        item.widget().close()
        # insert the selected editor
        de = self._materialEditor[index.row()]
        layout.insertWidget(1, de)
        de.show()
        self._window.setWindowTitle(de.nameEdit.text())

    def _matEditorFinishedSlot(self, signal, ids):
        """Method for handling the button events in the solver settings\n
        signal = the button hit\n
        ids = ID of the equation set"""

        signalOK = False
        if(signal == dynamiceditor.MatTypes.MAT_OK or
           signal == dynamiceditor.MatTypes.MAT_APPLY):
            signalOK = True

        if signalOK:
            # retrieve material name
            de = self._materialEditor[ids]
            matName = str(de.nameEdit.text()).strip()
            if not matName:
                sys.stdout.write("Material Name\n")
                sys.stdout.flush()
                return
            else:
                # update the list view item
                item = self._listview.item(ids)
                item.setText(matName)
                self._window.setWindowTitle(matName)
                if signal == dynamiceditor.MatTypes.MAT_OK:
                    self._window.close()

        elif signal == dynamiceditor.MatTypes.MAT_NEW:
            # create a new material
            # get window and layout
            window = self._window
            layout = window.layout()

            # new instance of the dynamic editor
            current = len(self._materialEditor)
            de = dynamiceditor.DynamicEditor()
            self._materialEditor.append(de)
            de.setupTabs(self._elmerDefs, "Material", current)
            de.applyButton.setText("Apply")
            de.discardButton.setText("Delete")
            de.dynamicEditorReady[int, int].connect(self._matEditorFinishedSlot)
            de.spareButton.setText("Show Material Library")
            de.spareButton.show()
            de.dynamicEditorSpareButtonClicked[int, int].connect(self._showMaterialLibrary)

            # clear right side of layout and at the new dynamic editor
            item = layout.takeAt(1)
            if item is not None:
                item.widget().close()
            layout.addWidget(de)

            # add item to list
            item = QtGui.QListWidgetItem()
            item.setText(de.nameEdit.text())
            self._listview.addItem(item)
            self._window.setWindowTitle(de.nameEdit.text())

        elif signal == dynamiceditor.MatTypes.MAT_DELETE:
            # Remove the current material editor from the collection
            if ids > 0:
                # remove the current equation
                item = self._listview.takeItem(ids)
                del self._materialEditor[ids]
                # show the previous equation
                layout = self._window.layout()
                item = layout.takeAt(1)
                item.widget().close()
                de = self._materialEditor[ids - 1]
                layout.insertWidget(1, de)
                self._window.setWindowTitle(de.nameEdit.text())
                de.show()
            else:
                # remove the current equation, last one
                del self._materialEditor[ids]
                self._materialEditor = []
                self._window.close()

    def _showMaterialLibrary(self, current, ids):
        return

    def _pdeEditorFinishedSlot(self, signal, ids):
        """Method for handling the button events in the solver settings\n
        signal = the button hit\n
        ids = ID of the equation set"""

        signalOK = False
        if(signal == dynamiceditor.MatTypes.MAT_OK or
           signal == dynamiceditor.MatTypes.MAT_APPLY):
            signalOK = True

        if signalOK:
            # get current equation name
            de = self._equationEditor[ids]
            equationName = str(de.nameEdit.text()).strip()
            if not equationName:
                sys.stdout.write("No equation name\n")
                sys.stdout.flush()
                return
            else:
                # update list view item
                item = self._listview.item(ids)
                item.setText(equationName)
                self._window.setWindowTitle(equationName)
                if signal == dynamiceditor.MatTypes.MAT_OK:
                    self._window.close()

        elif signal == dynamiceditor.MatTypes.MAT_NEW:
            # create new equation
            # get window and layout
            window = self._window
            layout = window.layout()

            # new instance of the dynamic editor
            current = len(self._equationEditor)
            de = dynamiceditor.DynamicEditor()
            self._equationEditor.append(de)
            de.setupTabs(self._elmerDefs, "Equation", current)
            de.applyButton.setText("Apply")
            de.discardButton.setText("Delete")
            de.dynamicEditorReady[int, int].connect(self._pdeEditorFinishedSlot)
            de.spareButton.setText("Edit Solver Settings")
            de.spareButton.show()
            de.dynamicEditorSpareButtonClicked[int, int].connect(self._editNumericalMethods)

            # clear right side of layout and at the new dynamic editor
            item = layout.takeAt(1)
            if item is not None:
                item.widget().close()
            layout.addWidget(de)

            # add item to list
            item = QtGui.QListWidgetItem()
            item.setText(de.nameEdit.text())
            self._listview.addItem(item)
            self._window.setWindowTitle(de.nameEdit.text())

        elif signal == dynamiceditor.MatTypes.MAT_DELETE:
            # Remove the current equation editor from the collection
            if ids > 0:
                # remove the current equation
                item = self._listview.takeItem(ids)
                del self._equationEditor[ids]
                # show the previous equation
                self._listview.item(ids-1).setSelected(True)
                layout = self._window.layout()
                item = layout.takeAt(1)
                item.widget().close()
                de = self._equationEditor[ids - 1]
                layout.insertWidget(1, de)
                self._window.setWindowTitle(de.nameEdit.text())
                de.show()
            else:
                # remove the current equation, last one
                del self._equationEditor[ids]
                self._equationEditor = []
                self._window.close()

    def _editNumericalMethods(self, current, ids):
        """Edit the solver specific properties\n
        current = ID of the equation set that should be edited"""

        title = ""
        for i in range(0, len(self._equationEditor)):
            title = self._equationEditor[i].tabWidget.tabText(current)
            break

        if title == "General":
            sys.stdout.write("No solver controls for 'General' equation options")
            sys.stdout.flush()
            return

        if current >= len(self._solverParameterEditor):
            self._solverParameterEditor.append(solverparameters.SovlerParameterEditor(path_forms))

        spe = self._solverParameterEditor[current]
        spe.setWindowTitle("Solver control for {}".format(title))
        spe.solverName = title

        if spe.generalOptions is None:
            spe.generalOptions = dynamiceditor.DynamicEditor()
            spe.generalOptions.setupTabs(self._elmerDefs, "Solver", current)
            spe.solverControlTabs.insertTab(0, spe.generalOptions.tabWidget.widget(current),
                                            "Solver specific options")

        for i in range(0, spe.generalOptions.tabWidget.count()):
            if spe.generalOptions.tabWidget.tabText(i) == title:
                spe.solverControlTabs.insertTab(0, spe.generalOptions.tabWidget.widget(i),
                                                "Solver specific options")
                break

        spe.show()

    def _xmlMerge(self, path):
        """Merges all edf-xml files in the given directory into a temporary file\n
        returns the temporary file object with the cursor at the beginning"""

        # temporary file
        mybuf = tempfile.TemporaryFile()

        gen_file = path + "edf.xml"

        # xml stream
        first = et.parse(gen_file).getroot()

        # get all edf files
        xml_files = glob.glob(path + "*.xml")
        xml_files = [file for file in xml_files
                     if not os.path.basename(file).startswith("edf")]

        # append each data to the xml stream
        for xml_file in xml_files:
            data = et.parse(xml_file).getroot()
            first.extend(data)

        # write xml stream to temporary file, set cursor to beginning
        mybuf.write(et.tostring(first))
        mybuf.seek(0)
        # read temp file and decode it properly into string
        temp = mybuf.read().decode()
        mybuf.close()

        # set the temp string as content of the QDomDocument
        self._elmerDefs = QtXml.QDomDocument()
        self._elmerDefs.setContent(temp)

if __name__ == "__main__":
    path = os.path.dirname(os.path.abspath(__file__))
    path_forms = path + "\\forms\\"
    path_edfs = path + "\\edf\\"
    sys.path.append(r"C:\opt\SALOME-7.8.0-WIN64\PLUGINS\ElmerSalome")
    app = QtGui.QApplication(sys.argv)
    ewh = elmerWindowHandler()
#    be = ewh.showBodyPropertyDefinition("teset")
    ewh.showAddEquation()
    ewh._window.close()
    ewh.showAddEquation()
    #sp = ewh.showSolverParametersEditor()
    #sp.show()
    sys.exit(app.exec_())