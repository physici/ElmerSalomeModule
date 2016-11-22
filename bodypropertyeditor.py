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
    """BodyPropertyEditor base class"""
    
    # signal
    bodyPropertyEditorApply = QtCore.pyqtSignal(QtGui.QDialog, str,
                                                name="bodyPropertyEditorApply")

    def __init__(self, path_forms):
        """Constructor"""

        # initialize base class
        super(BodyPropertyEditor, self).__init__()

        uic.loadUi(path_forms + "bodypropertyeditor.ui", self)

        #public fields
        self.material = None
        self.initial = None
        self.force = None
        self.equation = None

        #signals
        self.applyButton.clicked.connect(self._applySlot)
        self.discardButton.clicked.connect(self._discardSlot)
        self.materialCombo.currentIndexChanged.connect(self.materialComboChanged)
        self.initialConditionCombo.currentIndexChanged.connect(self.initialComboChanged)        
        self.bodyForceCombo.currentIndexChanged.connect(self.forceComboChanged)        
        self.equationCombo.currentIndexChanged.connect(self.equationComboChanged)  

    def _applySlot(self):
        self.bodyPropertyEditorApply.emit(self, str(self.nameEdit.text()))
        self.close()

    def _discardSlot(self):
        self.close()

    def materialComboChanged(self, select):
        self.material = self.materialCombo.itemData(select)

    def initialComboChanged(self, select):
        self.initial = self.initialConditionCombo.itemData(select)

    def forceComboChanged(self, select):
        self.force = self.bodyForceCombo.itemData(select)

    def equationComboChanged(self, select):
        self.equation = self.equationCombo.itemData(select)
