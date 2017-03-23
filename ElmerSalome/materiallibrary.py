# -*- coding: utf-8 -*-

try:
    from PyQt4 import QtGui
    from PyQt4 import QtXml
    from PyQt4 import QtCore
    from PyQt4 import uic
except ImportError:
    from PyQt5 import QtWidgets as QtGui
    from PyQt5 import QtXml
    from PyQt5 import QtCore
    from PyQt5 import uic


class MaterialLibrary(QtGui.QDialog):
    """Material library"""

    def __init__(self, path_forms, path_edfs):
        """Constructor

        Args:
        -----
        path_forms: str
            path to ui-interface directory
        path_edfs: str
            path to the xml-files directory
        """
        super(MaterialLibrary, self).__init__()

        # public
        self.editor = None
        self.elmerDefs = None

        # privat
        self._materialDoc = QtXml.QDomDocument()

        uic.loadUi(path_forms + "materiallibrary.ui", self)

        # connect buttons
        self.okButton.clicked.connect(self._okButtonClicked)
        self.appendButton.clicked.connect(self._appendButtonClicked)
        self.clearButton.clicked.connect(self._clearButtonClicked)
        self.closeButton.clicked.connect(self._closeButtonClicked)

        # load material library
        matFileName = path_edfs + "egmaterials.xml"
        matlist = self.materialListWidget
        matlist.clear()

        self._appendDocument(matFileName)

        self.materialListWidget.itemDoubleClicked.connect(self._itemDoubleClicked)

    def _okButtonClicked(self):
        """Ok-Button"""
        matlist = self.materialListWidget
        item = matlist.currentItem()

        if(item is None):
            return

        # get active material editor
        editor = self.editor

        # clear all lineEdits
        for key, value in editor.qhash.items():
            elem = value.elem
            widget = value.widget
            if(elem.attribute("Widget") == "Edit"):
                widget.setText("")

        # update lineEdts with library properties
        contents = self._materialDoc.documentElement()
        material = contents.firstChildElement("material")
        while(material.isNull() is False):
            materialName = str(material.attribute("name"))

            if(materialName != item.text()):
                material = material.nextSiblingElement()
                continue

            editor.nameEdit.setText(materialName)
            prop = material.firstChildElement()
            while(prop.isNull() is False):
                propertyName = str(prop.attribute("name")).strip().lower()
                propertyValue = str(prop.text()).strip()

                match = False

                for key, value in editor.qhash.items():
                    elem = value.elem
                    widget = value.widget
                    widgetName = str(elem.firstChildElement("Name").text()).strip().lower()

                    if(elem.attribute("Widget") == "Edit"):
                        if(propertyName == widgetName):
                            match = True
                            widget.setText(propertyValue)

                    if(elem.attribute("Widget") == "Combo"):
                        if(propertyName == widgetName):
                            for i in range(widget.count()):
                                itemText = str(widget.itemText(i)).strip()
                                if(itemText.lower() == propertyValue.lower()):
                                    widget.setCurrentIndex(i)
                            match = True

                prop = prop.nextSiblingElement()
            material = material.nextSiblingElement()

        self.close()
        self.editor.raise_()

    def _itemDoubleClicked(self, item):
        """Double click on list element"""
        matlist = self.materialListWidget
        matlist.setCurrentItem(item)
        self._okButtonClicked()

    def _appendButtonClicked(self):
        """AppendButton clicked"""
        matFileName = QtGui.QFileDialog.getOpenFileName(self)

        if(matFileName == ""):
            return

        self._materialDoc = QtXml.QDomElement()
        self._appendDocument(matFileName)

    def _clearButtonClicked(self):
        """Clear Button clicked"""
        matlist = self.materialListWidget
        matlist.clear()

    def _closeButtonClicked(self):
        self.close()
        self.editor.raise_()

    def _appendDocument(self, matFileName):
        """Append new document to material library"""
        materialFile = QtCore.QFile(matFileName)

        errStr = ""
        errRow = 0
        errCol = 0

        if(not materialFile.exists()):
            QtGui.QMessageBox.information(None, "Material loader",
                                          "Material library does not exist")
            return
        else:
            statusOK, errStr, errRow, errCol = self._materialDoc.setContent(materialFile, True)
            if(not statusOK):
                QtGui.QMessageBox.information(None, "Material loader",
                                              "Parse error at line {}, col {}:\n{}".format(errRow, errCol, errStr))
                materialFile.close()
                return

        materialFile.close()

        if(self._materialDoc.documentElement().tagName() != "materiallibrary"):
            QtGui.QMessageBox.information(None, "Material loader",
                                          "This is not a material library file")
            return

        # update list entries
        matlist = self.materialListWidget
        contents = self._materialDoc.documentElement()
        material = contents.firstChildElement("material")
        while(material.isNull() is False):
            materialName = material.attribute("name")
            matlist.addItem(materialName)
            material = material.nextSiblingElement()
        matlist.sortItems()
