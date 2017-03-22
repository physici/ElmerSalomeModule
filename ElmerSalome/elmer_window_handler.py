# -*- coding: utf-8 -*-
"""
Created on Sat Sep  3 14:31:15 2016

@author: Rainer Jacob
"""

from PyQt4 import QtGui
from PyQt4 import QtXml
from PyQt4 import QtCore

import os
import os.path
import sys
import glob
import tempfile

from xml.etree import ElementTree as et

import solverparameters
import generalsetup
import dynamiceditor
import bodypropertyeditor
import boundarypropertyeditor
import materiallibrary
import sifwrite

path = os.path.dirname(os.path.abspath(__file__))
path_forms = path + os.sep + "forms" + os.sep
path_edfs = path + os.sep + "edf" + os.sep

main = None


class ElmerWindowHandler():

    def __init__(self):
        """Constructor"""
        # public fields
        self.meshDirectory = ''
        # private fields
        self._equationEditor = []
        self._materialEditor = []
        self._solverParameterEditor = []
        self._bodyForceEditor = []
        self._initialConditionEditor = []
        self._boundaryConditionEditor = []
        self._elementProperties = {}
        self._materialLibrary = materiallibrary.MaterialLibrary(path_forms, path_edfs)
        self._elmerDefs = None
        self._listview = None
        self._window = None
        self._eqWindow = None
        self._matWindow = None
        self._bfWindow = None
        self._bcWindow = None
        self._icWindow = None
        self._gsWindow = None
        self._matCurrent = 0
        self._eqCurrent = 0
        self._bfCurrent = 0
        self._bcCurrent = 0
        self._icCurrent = 0
        self._xmlMerge(path_edfs)
        self._parent = self
        
        self._initGeneralSetup()

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

        # populate comboboxes
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

        # connect to slot
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

        # connect to slot
        be.bodyPropertyEditorApply.connect(self._bodyPropertyChanged)

        be.show()
        self._window = be
        return self._window
        
    def _initGeneralSetup(self):
        ge = generalsetup.GeneralSetup(path_forms)
        self._gsWindow = ge
        return ge

    def showGeneralSetup(self):
        """Initialize an instance of GeneralSetup and returns it to Salome"""
        if self._gsWindow is None:
            #ge = generalsetup.GeneralSetup(path_forms)
            ge = self.initGeneralSetup()
            ge.show()
            return ge
        else:
            self._gsWindow.show()
            return self._gsWindow

    def showSolverParametersEditor(self):
        """Initialize an instance of Solver Param Editor and returns it to Salome"""
        sp = solverparameters.SolverParameterEditor(path_forms)
        return sp

    def showAddEquation(self):
        """Creates a new instance of the dynamic editor for adding an equation"""
        # create a horizontal split layout
        if not self._eqWindow:
            self._eqWindow = QtGui.QWidget()
            layout = QtGui.QHBoxLayout()
            self._listview = QtGui.QListWidget()
            self._listview.clicked[QtCore.QModelIndex].connect(self._eqItemChanged)
            self._listview.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
            layout.addWidget(self._listview, stretch=1)
            self._eqWindow.setLayout(layout)
            self._pdeEditorFinishedSlot(dynamiceditor.MatTypes.MAT_NEW, 0)
            # create default solver settings
            for idx in range(self._equationEditor[0].tabWidget.count()):
                self._editNumericalMethods(idx, 0, False)
            self._eqWindow.show()
        else:
            self._eqWindow.show()

        return self._eqWindow

    def showAddMaterial(self):
        """Creates a new instance of the dynamic editor for adding a material"""
        if not self._matWindow:
            # create a horizontal split layout
            self._matWindow = QtGui.QWidget()
            layout = QtGui.QHBoxLayout()
            self._listview = QtGui.QListWidget()
            self._listview.clicked[QtCore.QModelIndex].connect(self._matItemChanged)
            self._listview.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
            layout.addWidget(self._listview, stretch=1)
            self._matWindow.setWindowTitle("Material Library")
            self._matWindow.setLayout(layout)
            self._matEditorFinishedSlot(dynamiceditor.MatTypes.MAT_NEW, 0)
            self._matWindow.show()
        else:
            self._matWindow.show()

        return self._matWindow

    def showAddBodyForce(self):
        """Creates a new instance of the dynamic editor for adding a body force"""
        if not self._bfWindow:
            # create a horizontal split layout
            self._bfWindow = QtGui.QWidget()
            layout = QtGui.QHBoxLayout()
            self._listview = QtGui.QListWidget()
            self._listview.clicked[QtCore.QModelIndex].connect(self._bfItemChanged)
            self._listview.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
            layout.addWidget(self._listview, stretch=1)
            self._bfWindow.setWindowTitle("Body force settings")
            self._bfWindow.setLayout(layout)
            self._bodyForceEditorFinishedSlot(dynamiceditor.MatTypes.MAT_NEW, 0)
            self._bfWindow.show()
        else:
            self._bfWindow.show()

        return self._bfWindow

    def showAddInitialCondition(self):
        """Creates a new instance of the dynamic editor for adding a initial condition"""
        if not self._icWindow:
            # create a horizontal split layout
            self._icWindow = QtGui.QWidget()
            layout = QtGui.QHBoxLayout()
            self._listview = QtGui.QListWidget()
            self._listview.clicked[QtCore.QModelIndex].connect(self._icItemChanged)
            self._listview.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
            layout.addWidget(self._listview, stretch=1)
            self._icWindow.setWindowTitle("Initial Condition settings")
            self._icWindow.setLayout(layout)
            self._initialConditionEditorFinishedSlot(dynamiceditor.MatTypes.MAT_NEW, 0)
            self._icWindow.show()
        else:
            self._icWindow.show()

        return self._icWindow

    def showAddBoundaryCondition(self):
        """Creates a new instance of the dynamic editor for adding a boundary condition"""
        if not self._bcWindow:
            # create a horizontal split layout
            self._bcWindow = QtGui.QWidget()
            layout = QtGui.QHBoxLayout()
            self._listview = QtGui.QListWidget()
            self._listview.clicked[QtCore.QModelIndex].connect(self._bcItemChanged)
            self._listview.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
            layout.addWidget(self._listview, stretch=1)
            self._bcWindow.setWindowTitle("Boundary Condition settings")
            self._bcWindow.setLayout(layout)
            self._boundaryConditionEditorFinishedSlot(dynamiceditor.MatTypes.MAT_NEW, 0)
            self._bcWindow.show()
        else:
            self._bcWindow.show()

        return self._bcWindow

    def _boundaryPropertyChanged(self, boundaryPropertyEditor, name):
        """Signal when body properties have changed"""
        self._elementProperties.update({str(name): boundaryPropertyEditor})

    def _bodyPropertyChanged(self, bodyPropertyEditor, name):
        """Signal when body properties have changed"""
        self._elementProperties.update({str(name): bodyPropertyEditor})

    def _eqItemChanged(self, index):
        """Method for changing the selected item in the equation editor view"""
        # delete second item == editor
        layout = self._eqWindow.layout()
        item = layout.takeAt(1)
        if item:
            item.widget().close()
        # insert the selected editor
        de = self._equationEditor[index.row()]
        de.show()
        layout.insertWidget(1, de, stretch=5)
        self._eqWindow.setWindowTitle(de.nameEdit.text())

    def _matItemChanged(self, index):
        """Method for changing the selected item in the material editor view"""
        # delete second item == editor
        layout = self._matWindow.layout()
        item = layout.takeAt(1)
        item.widget().close()
        # insert the selected editor
        de = self._materialEditor[index.row()]
        layout.insertWidget(1, de, stretch=5)
        de.show()
        self._matWindow.setWindowTitle(de.nameEdit.text())

    def _bfItemChanged(self, index):
        """Method for changing the selected item in the body force editor view"""
        # delete second item == editor
        layout = self._bfWindow.layout()
        item = layout.takeAt(1)
        item.widget().close()
        # insert the selected editor
        de = self._bodyForceEditor[index.row()]
        layout.insertWidget(1, de, stretch=5)
        de.show()
        self._bfWindow.setWindowTitle(de.nameEdit.text())

    def _icItemChanged(self, index):
        """Method for changing the selected item in the initial condition view"""
        # delete second item == editor
        layout = self._icWindow.layout()
        item = layout.takeAt(1)
        item.widget().close()
        # insert the selected editor
        de = self._initialConditionEditor[index.row()]
        layout.insertWidget(1, de, stretch=5)
        de.show()
        self._icWindow.setWindowTitle(de.nameEdit.text())

    def _bcItemChanged(self, index):
        """Method for changing the selected item in the boundary condition view"""
        # delete second item == editor
        layout = self._bcWindow.layout()
        item = layout.takeAt(1)
        item.widget().close()
        # insert the selected editor
        de = self._boundaryConditionEditor[index.row()]
        layout.insertWidget(1, de, stretch=5)
        de.show()
        self._bcWindow.setWindowTitle(de.nameEdit.text())
        
    def _bodyForceEditorFinishedSlot(self, signal, ids):
        """Method for handling the button events in the body force settings\n
        signal = the button hit\n
        ids = ID of the body force set"""
        for bf in self._bodyForceEditor:
            temp = bf.ID
            if temp == ids:
                ids = self._bodyForceEditor.index(bf)
                break

        listview = self._listview

        signalOK = False
        if(signal == dynamiceditor.MatTypes.MAT_OK or
           signal == dynamiceditor.MatTypes.MAT_APPLY):
            signalOK = True

        if(signalOK):
            item = listview.item(ids)
            de = self._bodyForceEditor[ids]
            bfName = str(de.nameEdit.text()).strip()
            if not bfName:
                sys.stdout.write("Body force\n")
                sys.stdout.flush()
                return
            else:
                item.setText(bfName)
                self._bfWindow.setWindowTitle(bfName)
                if signal == dynamiceditor.MatTypes.MAT_OK:
                    # hide window, but keep contents in memory
                    self._bfWindow.hide()
        elif(signal == dynamiceditor.MatTypes.MAT_NEW):
            """Create a new body force"""
            # get window and layout
            window = self._bfWindow
            layout = window.layout()

            # new instance of the dynamic editor
            current = self._bfCurrent
            de = dynamiceditor.DynamicEditor()
            self._bodyForceEditor.append(de)
            de.setupTabs(self._elmerDefs, "BodyForce", current)
            de.applyButton.setText("Apply")
            de.discardButton.setText("Delete")
            de.dynamicEditorReady[int, int].connect(self._bodyForceEditorFinishedSlot)

            # clear right side of layout and at the new dynamic editor
            item = layout.takeAt(1)
            if item is not None:
                item.widget().close()
            layout.addWidget(de, stretch=5)
            # add item to list
            item = QtGui.QListWidgetItem()
            item.setText(de.nameEdit.text())
            self._listview.addItem(item)
            self._bfWindow.setWindowTitle(de.nameEdit.text())

            # set new as selected
            count = len(self._bodyForceEditor)
            self._listview.item(count - 1).setSelected(True)
            self._bfCurrent += 1
        elif(signal == dynamiceditor.MatTypes.MAT_DELETE):
            """Remove the current material editor from the collection"""
            if len(self._bodyForceEditor) > 1:
                # remove the current element
                item = self._listview.takeItem(ids)
                del self._bodyForceEditor[ids]

                # show the previous element
                if ids > 0:
                    ids -= 1
                self._listview.item(ids).setSelected(True)
                layout = self._bfWindow.layout()
                item = layout.takeAt(1)
                item.widget().close()
                de = self._bodyForceEditor[ids]
                layout.insertWidget(1, de, stretch=5)
                de.show()
                self._bfWindow.setWindowTitle(de.nameEdit.text())
            else:
                # remove the current element
                del self._bodyForceEditor[ids]
                self._bodyForceEditor = []
                self._bfWindow.hide()

    def _initialConditionEditorFinishedSlot(self, signal, ids):
        """Method for handling the button events in the initial condition settings\n
        signal = the button hit\n
        ids = ID of the initial condition set"""
        for ic in self._initialConditionEditor:
            temp = ic.ID
            if temp == ids:
                ids = self._initialConditionEditor.index(ic)
                break

        listview = self._listview

        signalOK = False
        if(signal == dynamiceditor.MatTypes.MAT_OK or
            signal == dynamiceditor.MatTypes.MAT_APPLY):
            signalOK = True

        if(signalOK):
            item = listview.item(ids)
            de = self._initialConditionEditor[ids]
            icName = str(de.nameEdit.text()).strip()
            if not icName:
                sys.stdout.write("Initial Condition\n")
                sys.stdout.flush()
                return
            else:
                item.setText(icName)
                self._icWindow.setWindowTitle(icName)
                if signal == dynamiceditor.MatTypes.MAT_OK:
                    # hide window, but keep contents in memory
                    self._icWindow.hide()
        elif(signal == dynamiceditor.MatTypes.MAT_NEW):
            """Create a new initial condition"""
            # get window and layout
            window = self._icWindow
            layout = window.layout()

            # new instance of the dynamic editor
            current = self._icCurrent
            de = dynamiceditor.DynamicEditor()
            self._initialConditionEditor.append(de)
            de.setupTabs(self._elmerDefs, "InitialCondition", current)
            de.applyButton.setText("Apply")
            de.discardButton.setText("Delete")
            de.dynamicEditorReady[int, int].connect(self._initialConditionEditorFinishedSlot)

            # clear right side of layout and at the new dynamic editor
            item = layout.takeAt(1)
            if item is not None:
                item.widget().close()
            layout.addWidget(de, stretch=5)
            # add item to list
            item = QtGui.QListWidgetItem()
            item.setText(de.nameEdit.text())
            self._listview.addItem(item)
            self._icWindow.setWindowTitle(de.nameEdit.text())

            # set new as selected
            count = len(self._initialConditionEditor)
            self._listview.item(count - 1).setSelected(True)
            self._icCurrent += 1
        elif(signal == dynamiceditor.MatTypes.MAT_DELETE):
            """Remove the current initial condition from the collection"""
            if len(self._initialConditionEditor) > 1:
                # remove the current equation
                item = self._listview.takeItem(ids)
                del self._initialConditionEditor[ids]

                # show the previous element
                if ids > 0:
                    ids -= 1
                self._listview.item(ids).setSelected(True)
                layout = self._icWindow.layout()
                item = layout.takeAt(1)
                item.widget().close()
                de = self._initialConditionEditor[ids]
                layout.insertWidget(1, de, stretch=5)
                de.show()
                self._icWindow.setWindowTitle(de.nameEdit.text())
            else:
                # remove the current element
                del self._initialConditionEditor[ids]
                self._initialConditionEditor = []
                self._icWindow.hide()

    def _boundaryConditionEditorFinishedSlot(self, signal, ids):
        """Method for handling the button events in the boundary condition settings\n
        signal = the button hit\n
        ids = ID of the boundary condition set"""
        for bc in self._boundaryConditionEditor:
            temp = bc.ID
            if temp == ids:
                ids = self._boundaryConditionEditor.index(bc)
                break

        listview = self._listview

        signalOK = False
        if(signal == dynamiceditor.MatTypes.MAT_OK or
            signal == dynamiceditor.MatTypes.MAT_APPLY):
            signalOK = True

        if(signalOK):
            item = listview.item(ids)
            de = self._boundaryConditionEditor[ids]
            bcName = str(de.nameEdit.text()).strip()
            if not bcName:
                sys.stdout.write("Boundary Condition\n")
                sys.stdout.flush()
                return
            else:
                item.setText(bcName)
                self._bcWindow.setWindowTitle(bcName)
                if signal == dynamiceditor.MatTypes.MAT_OK:
                    # hide window, but keep contents in memory
                    self._bcWindow.hide()
        elif(signal == dynamiceditor.MatTypes.MAT_NEW):
            """Create a new boundary condition"""
            # get window and layout
            window = self._bcWindow
            layout = window.layout()

            # new instance of the dynamic editor
            current = self._bcCurrent
            de = dynamiceditor.DynamicEditor()
            self._boundaryConditionEditor.append(de)
            de.setupTabs(self._elmerDefs, "BoundaryCondition", current)
            de.applyButton.setText("Apply")
            de.discardButton.setText("Delete")
            de.dynamicEditorReady[int, int].connect(self._boundaryConditionEditorFinishedSlot)

            # clear right side of layout and at the new dynamic editor
            item = layout.takeAt(1)
            if item is not None:
                item.widget().close()
            layout.addWidget(de, stretch=5)
            # add item to list
            item = QtGui.QListWidgetItem()
            item.setText(de.nameEdit.text())
            self._listview.addItem(item)
            self._bcWindow.setWindowTitle(de.nameEdit.text())

            # set new as selected
            count = len(self._boundaryConditionEditor)
            self._listview.item(count - 1).setSelected(True)
            self._bcCurrent += 1
        elif(signal == dynamiceditor.MatTypes.MAT_DELETE):
            """Remove the current boundary condition from the collection"""
            if len(self._boundaryConditionEditor) > 1:
                # remove the current equation
                item = self._listview.takeItem(ids)
                del self._boundaryConditionEditor[ids]

                # show the previous element
                if ids > 0:
                    ids -= 1
                self._listview.item(ids).setSelected(True)
                layout = self._bcWindow.layout()
                item = layout.takeAt(1)
                item.widget().close()
                de = self._boundaryConditionEditor[ids]
                layout.insertWidget(1, de, stretch=5)
                de.show()
                self._bcWindow.setWindowTitle(de.nameEdit.text())
            else:
                # remove the current element
                del self._boundaryConditionEditor[ids]
                self._boundaryConditionEditor = []
                self._bcWindow.hide()

    def _matEditorFinishedSlot(self, signal, ids):
        """Method for handling the button events in the materials settings\n
        signal = the button hit\n
        ids = ID of the material set"""
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
                    # hide window, but keep contents in memory
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

            # clear right side of layout and at the new dynamic editor
            item = layout.takeAt(1)
            if item is not None:
                item.widget().close()
            layout.addWidget(de, stretch=5)

            # add item to list
            item = QtGui.QListWidgetItem()
            item.setText(de.nameEdit.text())
            self._listview.addItem(item)
            self._matWindow.setWindowTitle(de.nameEdit.text())

            # set new as selected
            count = len(self._materialEditor)
            self._listview.item(count - 1).setSelected(True)
            self._matCurrent += 1
        elif(signal == dynamiceditor.MatTypes.MAT_DELETE):
            """Remove the current material editor from the collection"""
            if len(self._materialEditor) > 1:
                # remove the current element
                item = self._listview.takeItem(ids)
                del self._materialEditor[ids]

                # show the previous element
                if ids > 1:
                    ids -= 1
                self._listview.item(ids).setSelected(True)
                layout = self._matWindow.layout()
                item = layout.takeAt(1)
                item.widget().close()
                de = self._materialEditor[ids]
                layout.insertWidget(1, de, stretch=5)
                de.show()
                self._matWindow.setWindowTitle(de.nameEdit.text())
            else:
                # remove the current element
                del self._materialEditor[ids]
                self._materialEditor = []
                self._matWindow.hide()

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
                    # hide window, but keep contents in memory
                    self._eqWindow.hide()
        elif(signal == dynamiceditor.MatTypes.MAT_NEW):
            """Create a new equation"""
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

            # clear right side of layout and at the new dynamic editor
            item = layout.takeAt(1)
            if item is not None:
                item.widget().close()
            layout.addWidget(de, stretch=5)

            # add item to list
            item = QtGui.QListWidgetItem()
            item.setText(de.nameEdit.text())
            self._listview.addItem(item)

            # set new as selected
            count = len(self._equationEditor)
            self._listview.item(count - 1).setSelected(True)
            self._eqWindow.setWindowTitle(de.nameEdit.text())
            self._eqCurrent += 1
        elif(signal == dynamiceditor.MatTypes.MAT_DELETE):
            """Remove the current equation editor from the collection"""
            if len(self._equationEditor) > 1:
                # remove the current equation
                item = self._listview.takeItem(ids)
                del self._equationEditor[ids]

                # show the previous equation
                if ids > 0:
                    ids -= 1
                self._listview.item(ids).setSelected(True)
                layout = self._eqWindow.layout()
                item = layout.takeAt(1)
                item.widget().close()
                de = self._equationEditor[ids]
                layout.insertWidget(1, de, stretch=5)
                de.show()
                self._eqWindow.setWindowTitle(de.nameEdit.text())
            else:
                # remove the current equation
                del self._equationEditor[ids]
                self._equationEditor = []
                self._eqWindow.hide()

    def _showMaterialLibrary(self, current, ids):
        """Opens the material library and connects it to the currently
        active material"""
        self._materialLibrary.editor = self._materialEditor[ids]
        self._materialLibrary.elmerDefs = self._elmerDefs
        self._materialLibrary.show()

    def _editNumericalMethods(self, current, ids, show=True):
        """Edit the solver specific properties\n
        current = tab-index\n
        ids = id of the equation\n
        show = create window or not"""

        title = ""
        # get active tab in the currently opened equation set
        for eq in self._equationEditor:
            if eq.ID == ids:
                title = eq.tabWidget.tabText(current)
                break

        if(title == "General"):
            sys.stdout.write("No solver controls for 'General' equation options")
            sys.stdout.flush()
            return

        # if tab is not yet in list, resize list and copy previous items
        if(current >= len(self._solverParameterEditor)):
            tmp = (current + 1) * [None]
            for idx, element in enumerate(self._solverParameterEditor):
                tmp[idx] = element
            self._solverParameterEditor = tmp

        if not self._solverParameterEditor[current]:
            self._solverParameterEditor[current] = solverparameters.SolverParameterEditor(path_forms)

        spe = self._solverParameterEditor[current]
        spe.setWindowTitle("Solver control for {}".format(title))
        spe.solverName = title

        if(spe.generalOptions is None):
            spe.generalOptions = dynamiceditor.DynamicEditor()
            spe.generalOptions.setupTabs(self._elmerDefs, "Solver", current)
            spe.solverControlTabs.insertTab(0, spe.generalOptions.tabWidget.widget(current),
                                            "Solver specific options")

        for i in range(0, spe.generalOptions.tabWidget.count()):
            if(spe.generalOptions.tabWidget.tabText(i) == title):
                spe.solverControlTabs.insertTab(0, spe.generalOptions.tabWidget.widget(i),
                                            "Solver specific options")
                break

        if show:
            spe.show()

    def _xmlMerge(self, path):
        """Merges all edf-xml files in the given directory into a temporary file\n
        returns the temporary file object with the cursor at the beginning"""

        mybuf = tempfile.TemporaryFile()

        gen_file = path + "edf.xml"

        first = et.parse(gen_file).getroot()

        xml_files = glob.glob(path + "*.xml")
        xml_files = [file for file in xml_files if not os.path.basename(file).startswith("edf")]
        xml_files = [file for file in xml_files if not os.path.basename(file).startswith("eg")]

        for xml_file in xml_files:
            data = et.parse(xml_file).getroot()
            first.extend(data)

        mybuf.write(et.tostring(first))
        mybuf.seek(0)
        temp = mybuf.read().decode()
        mybuf.close()

        self._elmerDefs = QtXml.QDomDocument()
        self._elmerDefs.setContent(temp)
        
    def sif_write(self):
        sfw = sifwrite.SifWriter(self)
        if not self.meshDirectory:
            d = str(QtGui.QFileDialog.getExistingDirectory(parent=None, caption="Select Directory"))
        if not d:
            return
        self.meshDirectory = os.path.normpath(d)
        sfw.file = self.meshDirectory + os.sep + 'simulation.sif'
        sfw.writeSif()
        


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
