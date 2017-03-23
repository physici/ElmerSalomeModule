# -*- coding: utf-8 -*-
"""
Created on Sun Oct 16 15:53:26 2016

@author: Rainer Jacob

Widget that allows setting of body properties
"""

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import uic


class BodyPropertyEditor(QtGui.QDialog):
    """Body property editor base class"""

    # signal changed
    bodyPropertyEditorApply = QtCore.pyqtSignal(QtGui.QDialog, str,
                                                name="bodyPropertyEditorApply")

    def __init__(self, path_forms):
        """Constructor.

        Args:
        -----
        path_forms: str
            String containing the path to the ui-files defining the look of the
            window.
        """
        super(BodyPropertyEditor, self).__init__()

        uic.loadUi(path_forms + "bodypropertyeditor.ui", self)

        # public
        self.material = None
        self.initial = None
        self.force = None
        self.equation = None

        # signals
        self.applyButton.clicked.connect(self._applySlot)
        self.discardButton.clicked.connect(self._discardSlot)
        self.materialCombo.currentIndexChanged.connect(self._materialComboChanged)
        self.initialConditionCombo.currentIndexChanged.connect(self._initialComboChanged)
        self.bodyForceCombo.currentIndexChanged.connect(self._forceComboChanged)
        self.equationCombo.currentIndexChanged.connect(self._equationComboChanged)

    def _applySlot(self):
        self.bodyPropertyEditorApply.emit(self, str(self.nameEdit.text()))
        self.close()

    def _discardSlot(self):
        self.close()

    def _materialComboChanged(self, select):
        self.material = self.materialCombo.itemText(select)

    def _initialComboChanged(self, select):
        self.initial = self.initialConditionCombo.itemText(select)

    def _forceComboChanged(self, select):
        self.force = self.bodyForceCombo.itemText(select)

    def _equationComboChanged(self, select):
        self.equation = self.equationCombo.itemText(select)
