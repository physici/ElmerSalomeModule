# -*- coding: utf-8 -*-
"""
Created on Sat Sep  3 14:31:15 2016

@author: Rainer Jacob
"""
try:
    from PyQt4 import QtGui
    from PyQt4 import QtXml
    from PyQt4 import QtCore
except ImportError:
    from PyQt5 import QtWidgets as QtGui
    from PyQt5 import QtXml
    from PyQt5 import QtCore

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
    """Main class of Elmer-plugin. Handles all calls and creates and stores
    windows. References to the windows have to be kept in memory otherwise
    they will not be shown properly."""

    def __init__(self):
        """Constructor"""
        # public fields
        self.meshDirectory = ''
        # private fields
        self._equationEditor = []  # stores the equations sets
        self._materialEditor = []  # stores the defined materials
        self._solverParameterEditor = []  # stores the specific solver settings
        self._bodyForceEditor = []  # stores the body forces
        self._initialConditionEditor = []  # stores the initial conditions
        self._boundaryConditionEditor = []  # stores the boundary conditions
        self._elementProperties = {}  # stores the properties of bodies/faces by name
        self._materialLibrary = materiallibrary.MaterialLibrary(path_forms, path_edfs)
        # storage variables to to keep track of windows
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

        # set the default general settings
        self._initGeneralSetup()

    def about(self):
        """Information window."""
        QtGui.QMessageBox.about(None, "About ELMER window handler",
                                        "Provides a handler to access ELMER configuration windows.\n" \
                                        "Requires ELMER, ELMERGUI and ELMER_HOME variable to be set.\n\n" \
                                        "Functionality provided only in Mesh-module.")

    def showBoundaryPropertyDefinition(self, objName):
        """Dialog to define boundary properties for an object.

        Args:
        -----
        objName: str
            String containing the name of the element as provided in Salome
            Object Browser

        Return:
        -------
        _window: BoundaryPropertyEditor-class
            BoundaryProperty-Window with the new data
        """
        # create new instance of BoundaryPropertyEditor-class
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
        # select first entry
        count = 1

        # check if element already has properties
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
        """Dialog to define body properties for an object.

        Args:
        -----
        objName: str
            String containing the name of the element as provided in Salome
            Object Browser

        Return:
        -------
        _window: BodyPropertyEditor-class
            BodyProperty-Window with the new data
        """
        # create new instance of BodyPropertyEditor-class
        be = bodypropertyeditor.BodyPropertyEditor(path_forms)
        be.nameEdit.setText(objName)
        be.setWindowTitle("Body property for body {}".format(objName))

        # populate comboboxes
        count = 1
        # equations
        be.equationCombo.addItem("", "Empty")
        count += 1
        for element in self._equationEditor:
            name = str(element.nameEdit.text()).strip()
            be.equationCombo.addItem(name, name)
            count += 1
        count = 1
        # materials
        be.materialCombo.addItem("", "Empty")
        count += 1
        for element in self._materialEditor:
            name = str(element.nameEdit.text()).strip()
            be.materialCombo.addItem(name, name)
            count += 1
        count = 1
        # body forces
        be.bodyForceCombo.addItem("", "Empty")
        count += 1
        for element in self._bodyForceEditor:
            name = str(element.nameEdit.text()).strip()
            be.bodyForceCombo.addItem(name, name)
            count += 1
        count = 1
        # initial conditions
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

    def showGeneralSetup(self):
        """Show general settings window

        Return:
        -------
        _gsWindow: GeneralSetup-class
            Window for the general settings
        """
        self._gsWindow.show()
        return self._gsWindow

    def showSolverParametersEditor(self):
        """Show Solver settings window

        Return:
        -------
        sp: SolverParameterEditor-class
            Window for the general settings
        """
        sp = solverparameters.SolverParameterEditor(path_forms)
        return sp

    def showAddEquation(self):
        """Show Equation settings window

        Return:
        -------
        _eqWindow: QtWidget
            QtWidget with listview and Equation settings section
        """
        if not self._eqWindow:
            # create a horizontal split layout
            self._eqWindow = QtGui.QWidget()
            layout = QtGui.QHBoxLayout()
            # create a listview-object
            self._listview = QtGui.QListWidget()
            self._listview.clicked[QtCore.QModelIndex].connect(self._eqItemChanged)
            self._listview.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
            # add listview to left layout-side
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
        """Show Material settings window

        Return:
        -------
        _matWindow: QtWidget
            QtWidget with listview and Materials settings section
        """
        if not self._matWindow:
            # create a horizontal split layout
            self._matWindow = QtGui.QWidget()
            layout = QtGui.QHBoxLayout()
            self._listview = QtGui.QListWidget()
            self._listview.clicked[QtCore.QModelIndex].connect(self._matItemChanged)
            self._listview.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
            # add listview to left layout-side
            layout.addWidget(self._listview, stretch=1)
            self._matWindow.setWindowTitle("Material Library")
            self._matWindow.setLayout(layout)
            self._matEditorFinishedSlot(dynamiceditor.MatTypes.MAT_NEW, 0)
            self._matWindow.show()
        else:
            self._matWindow.show()

        return self._matWindow

    def showAddBodyForce(self):
        """Show Body forces settings window

        Return:
        -------
        _bfWindow: QtWidget
            QtWidget with listview and Body forces settings section
        """
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
        """Show Initial conditions settings window

        Return:
        -------
        _icWindow: QtWidget
            QtWidget with listview and initial conditions settings section
        """
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
        """Show Boundary conditions settings window

        Return:
        -------
        _bcWindow: QtWidget
            QtWidget with listview and boundary settings section
        """
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

    def sif_write(self):
        """Sif file generator"""
        # create new instance of SifWriter-class
        sfw = sifwrite.SifWriter(self)
        # check if mesh export directory has been defined
        if not self.meshDirectory:
            d = str(QtGui.QFileDialog.getExistingDirectory(parent=None, caption="Select Directory"))
        if not d:
            return
        self.meshDirectory = os.path.normpath(d)
        sfw.file = self.meshDirectory + os.sep + 'simulation.sif'
        # generate sif file
        sfw.writeSif()

    def _initGeneralSetup(self):
        """Load the default general settings.

        Return:
        -------
        _gsWindow: GeneralSetup-class
            Window for the general settings
        """
        ge = generalsetup.GeneralSetup(path_forms)
        self._gsWindow = ge
        return ge

    def _boundaryPropertyChanged(self, boundaryPropertyEditor, name):
        """Signal when boundary properties of 'name' have changed.

        Args:
        -----
        boundaryPropertyEditor: BoundaryPropertyEditor-class
            The current boundary property
        name: str
            Name of the object whose boundary properties have been changed.
        """
        self._elementProperties.update({str(name): boundaryPropertyEditor})

    def _bodyPropertyChanged(self, bodyPropertyEditor, name):
        """Signal when body properties of 'name' have changed.

        Args:
        -----
        boundaryPropertyEditor: BodyPropertyEditor-class
            The current Body property
        name: str
            Name of the object whose body properties have been changed.
        """
        self._elementProperties.update({str(name): bodyPropertyEditor})

    def _eqItemChanged(self, index):
        """Method for changing the selected item in the equation editor view

        Args:
        -----
        index: QModelIndex
            index of the newly selected item.
        """
        # 'hide' the old editor == second element in layout
        layout = self._eqWindow.layout()
        item = layout.takeAt(1)
        if item:
            item.widget().close()
        # 'show' the new editor == insert the selected editor
        de = self._equationEditor[index.row()]
        de.show()
        layout.insertWidget(1, de, stretch=5)
        self._eqWindow.setWindowTitle(de.nameEdit.text())

    def _matItemChanged(self, index):
        """Method for changing the selected item in the material editor view

        Args:
        -----
        index: QModelIndex
            index of the newly selected item.
        """
        # 'hide' the old editor == second element in layout
        layout = self._matWindow.layout()
        item = layout.takeAt(1)
        item.widget().close()
        # 'show' the new editor == insert the selected editor
        de = self._materialEditor[index.row()]
        layout.insertWidget(1, de, stretch=5)
        de.show()
        self._matWindow.setWindowTitle(de.nameEdit.text())

    def _bfItemChanged(self, index):
        """Method for changing the selected item in the body force editor view

        Args:
        -----
        index: QModelIndex
            index of the newly selected item.
        """
        # 'hide' the old editor == second element in layout
        layout = self._bfWindow.layout()
        item = layout.takeAt(1)
        item.widget().close()
        # 'show' the new editor == insert the selected editor
        de = self._bodyForceEditor[index.row()]
        layout.insertWidget(1, de, stretch=5)
        de.show()
        self._bfWindow.setWindowTitle(de.nameEdit.text())

    def _icItemChanged(self, index):
        """Method for changing the selected item in the body force editor view

        Args:
        -----
        index: QModelIndex
            index of the newly selected item.
        """
        # 'hide' the old editor == second element in layout
        layout = self._icWindow.layout()
        item = layout.takeAt(1)
        item.widget().close()
        # 'show' the new editor == insert the selected editor
        de = self._initialConditionEditor[index.row()]
        layout.insertWidget(1, de, stretch=5)
        de.show()
        self._icWindow.setWindowTitle(de.nameEdit.text())

    def _bcItemChanged(self, index):
        """Method for changing the selected item in the boundary condition
        editor view

        Args:
        -----
        index: QModelIndex
            index of the newly selected item.
        """
        # 'hide' the old editor == second element in layout
        layout = self._bcWindow.layout()
        item = layout.takeAt(1)
        item.widget().close()
        # 'show' the new editor == insert the selected editor
        de = self._boundaryConditionEditor[index.row()]
        layout.insertWidget(1, de, stretch=5)
        de.show()
        self._bcWindow.setWindowTitle(de.nameEdit.text())

    def _bodyForceEditorFinishedSlot(self, signal, ids):
        """Method for handling the button events in the body force settings.

        Args:
        -----
        signal: int
            Type of button clicked
        ids: int
            ID of the body force set
        """
        # check if already in the storage and retrieve it
        for bf in self._bodyForceEditor:
            temp = bf.ID
            if temp == ids:
                ids = self._bodyForceEditor.index(bf)
                break

        listview = self._listview

        # check OK-Button or Apply-Button
        signalOK = False
        if(signal == dynamiceditor.MatTypes.MAT_OK or
           signal == dynamiceditor.MatTypes.MAT_APPLY):
            signalOK = True

        # OK or Apply
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
                # hide window, when OK
                if signal == dynamiceditor.MatTypes.MAT_OK:
                    self._bfWindow.hide()
        # New -> create new Body Force
        elif(signal == dynamiceditor.MatTypes.MAT_NEW):
            # get window and layout
            window = self._bfWindow
            layout = window.layout()

            # new instance of the dynamic editor
            current = self._bfCurrent
            de = dynamiceditor.DynamicEditor()
            # put new instance into storage
            self._bodyForceEditor.append(de)
            # populate tabs
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
        # Delete
        elif(signal == dynamiceditor.MatTypes.MAT_DELETE):
            # remove the current body force
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
                # remove the last element
                del self._bodyForceEditor[ids]
                self._bodyForceEditor = []
                # close the window
                self._bfWindow.hide()

    def _initialConditionEditorFinishedSlot(self, signal, ids):
        """Method for handling the button events in the initial condition
        settings.

        Args:
        -----
        signal: int
            Type of button clicked
        ids: int
            ID of the body force set
        """
        # check if already in the storage and retrieve it
        for ic in self._initialConditionEditor:
            temp = ic.ID
            if temp == ids:
                ids = self._initialConditionEditor.index(ic)
                break

        listview = self._listview

        # check OK-Button or Apply-Button
        signalOK = False
        if(signal == dynamiceditor.MatTypes.MAT_OK or
           signal == dynamiceditor.MatTypes.MAT_APPLY):
            signalOK = True

        # OK or Apply
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
                # hide window, when OK
                if signal == dynamiceditor.MatTypes.MAT_OK:
                    self._icWindow.hide()
        # New -> create new Initial condition
        elif(signal == dynamiceditor.MatTypes.MAT_NEW):
            # get window and layout
            window = self._icWindow
            layout = window.layout()

            # new instance of the dynamic editor
            current = self._icCurrent
            de = dynamiceditor.DynamicEditor()
            # put new instance into storage
            self._initialConditionEditor.append(de)
            # populate tabs
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
        # Delete
        elif(signal == dynamiceditor.MatTypes.MAT_DELETE):
            # remove the current initial condition
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
                # remove the last element
                del self._initialConditionEditor[ids]
                self._initialConditionEditor = []
                # close the window
                self._icWindow.hide()

    def _boundaryConditionEditorFinishedSlot(self, signal, ids):
        """Method for handling the button events in the boundary condition
        settings.

        Args:
        -----
        signal: int
            Type of button clicked
        ids: int
            ID of the body force set
        """
        # check if already in the storage and retrieve it
        for bc in self._boundaryConditionEditor:
            temp = bc.ID
            if temp == ids:
                ids = self._boundaryConditionEditor.index(bc)
                break

        listview = self._listview

        # check OK-Button or Apply-Button
        signalOK = False
        if(signal == dynamiceditor.MatTypes.MAT_OK or
           signal == dynamiceditor.MatTypes.MAT_APPLY):
            signalOK = True

        # OK or Apply
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
                # hide window, when OK
                if signal == dynamiceditor.MatTypes.MAT_OK:
                    self._bcWindow.hide()
        # New -> create new boundary condition
        elif(signal == dynamiceditor.MatTypes.MAT_NEW):
            # get window and layout
            window = self._bcWindow
            layout = window.layout()

            # new instance of the dynamic editor
            current = self._bcCurrent
            de = dynamiceditor.DynamicEditor()
            # put new instance into storage
            self._boundaryConditionEditor.append(de)
            # populate tabs
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
        # Delete
        elif(signal == dynamiceditor.MatTypes.MAT_DELETE):
            # remove the current boundary condition
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
                # remove the last element
                del self._boundaryConditionEditor[ids]
                self._boundaryConditionEditor = []
                # close the window
                self._bcWindow.hide()

    def _matEditorFinishedSlot(self, signal, ids):
        """Method for handling the button events in the material settings.

        Args:
        -----
        signal: int
            Type of button clicked
        ids: int
            ID of the body force set
        """
        # check if already in the storage and retrieve it
        for mat in self._materialEditor:
            temp = mat.ID
            if temp == ids:
                ids = self._materialEditor.index(mat)
                break

        listview = self._listview

        # check OK-Button or Apply-Button
        signalOK = False
        if(signal == dynamiceditor.MatTypes.MAT_OK or
           signal == dynamiceditor.MatTypes.MAT_APPLY):
            signalOK = True

        # OK or Apply
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
                # hide window, when OK
                if signal == dynamiceditor.MatTypes.MAT_OK:
                    self._matWindow.hide()
        # New -> create new Material
        elif(signal == dynamiceditor.MatTypes.MAT_NEW):
            # get window and layout
            window = self._matWindow
            layout = window.layout()

            # new instance of the dynamic editor
            current = self._matCurrent
            de = dynamiceditor.DynamicEditor()
            # put new instance into storage
            self._materialEditor.append(de)
            # populate tabs
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
        # Delete
        elif(signal == dynamiceditor.MatTypes.MAT_DELETE):
            # remove the current material
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
                # close the window
                self._matWindow.hide()

    def _pdeEditorFinishedSlot(self, signal, ids):
        """Method for handling the button events in the equation settings.

        Args:
        -----
        signal: int
            Type of button clicked
        ids: int
            ID of the body force set
        """
        # check if already in the storage and retrieve it
        for eq in self._equationEditor:
            temp = eq.ID
            if temp == ids:
                ids = self._equationEditor.index(eq)
                break

        listview = self._listview

        # check OK-Button or Apply-Button
        signalOK = False
        if(signal == dynamiceditor.MatTypes.MAT_OK or
           signal == dynamiceditor.MatTypes.MAT_APPLY):
            signalOK = True

        # OK or Apply
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
                # hide window, when OK
                if signal == dynamiceditor.MatTypes.MAT_OK:
                    self._eqWindow.hide()
        # New -> create new Equation
        elif(signal == dynamiceditor.MatTypes.MAT_NEW):
            # get window and layout
            window = self._eqWindow
            layout = window.layout()

            # new instance of the dynamic editor
            current = self._eqCurrent
            de = dynamiceditor.DynamicEditor()
            # put new instance into storage
            self._equationEditor.append(de)
            # populate tabs
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
        # Delete
        elif(signal == dynamiceditor.MatTypes.MAT_DELETE):
            # remove the current equation editor
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
                # close the window
                self._eqWindow.hide()

    def _showMaterialLibrary(self, current, ids):
        """Opens the material library and connects it to the currently
        active material

        Args:
        -----
        current: int
            Index of the current material
        ids: int
            ID of the current material
        """
        self._materialLibrary.editor = self._materialEditor[ids]
        self._materialLibrary.elmerDefs = self._elmerDefs
        self._materialLibrary.show()

    def _editNumericalMethods(self, current, ids, show=True):
        """Edit the solver specific properties

        Args:
        -----
        current: int
            current tab-index
        ids: int
            ID of the equation
        show: bool
            flag to show window or not
        """

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
        # create a new instane of the Solver settings and put it into storage
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
        """Merges all edf-xml files in the given directory into a temporary
        file

        Args:
        -----
        path: str
            path to the Elmer xml-files configuration files

        """
        # create a temporary file
        mybuf = tempfile.TemporaryFile()

        gen_file = path + "edf.xml"

        # general settings
        first = et.parse(gen_file).getroot()

        # solver settings
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
