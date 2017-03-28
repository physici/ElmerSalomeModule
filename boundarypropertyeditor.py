# -*- coding: utf-8 -*-
"""
Created on Sun Oct 16 16:49:42 2016

@author: Rainer Jacob

Boundary property editor class
"""

try:
    from PyQt4 import QtGui
    from PyQt4 import QtCore
    from PyQt4 import uic
except ImportError:
    from PyQt5 import QtWidgets as QtGui
    from PyQt5 import QtCore
    from PyQt5 import uic


class BoundaryPropertyEditor(QtGui.QDialog):
    """Boundary Property base class"""

    # signal changed
    boundaryPropertyEditorApply = QtCore.pyqtSignal(QtGui.QDialog, str,
                                                    name="boundaryPropertyEditorApply")

    def __init__(self, path_forms):
        """Constructor.

        Args:
        -----
        path_forms: str
            String containing the path to the ui-files defining the look of the
            window.
        """
        super(BoundaryPropertyEditor, self).__init__()

        uic.loadUi(path_forms + "boundarypropertyeditor.ui", self)

        self.bodyCondition = 0
        self.objName = None
        self.boundaryProperties = None

        # signals
        self.applyButton.clicked.connect(self._applySlot)
        self.discardButton.clicked.connect(self._discardSlot)
        self.boundaryAsABody.stateChanged.connect(self._boundaryAsBodyChanged)
        self.boundaryConditionCombo.currentIndexChanged.connect(self._boundaryComboChanged)

    def _applySlot(self):
        self.boundaryPropertyEditorApply.emit(self, self.objName)
        self.close()

    def _discardSlot(self):
        self.close()

    def _boundaryAsBodyChanged(self):
        self.bodyCondition = int(self.boundaryAsABody.checkState())
        print(self.bodyCondition)

    def _boundaryComboChanged(self, select):
        self.boundaryProperties = self.boundaryConditionCombo.itemText(select)
