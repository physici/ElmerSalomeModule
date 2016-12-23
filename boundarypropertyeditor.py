# -*- coding: utf-8 -*-
"""
Created on Sun Oct 16 16:49:42 2016

@author: Rainer Jacob

Boundary property editor class
"""

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import uic


class BoundaryPropertyEditor(QtCore.QDialog):
    """BoundaryPropertyEditor base class"""

    def __init__(self, path_forms):
        """Constructor"""

        # initialize base class
        super(BoundaryPropertyEditor, self).__init__()

        uic.loadUi(path_forms + "BoundaryPropertyEditor.ui", self)

        # public fields
        self.touched = False
        self.condition = None
        self.bodyProperties = None

        # signals
        self.applyButton.clicked.connect(self._applySlot)
        self.discardButton.clicked.connect(self._discardSlot)
        self.boundaryAsABody.stateChanged.connect(self.boundaryAsABodyChanged)
        self.boundaryConditionCombo.currentIndexChanged.connect(self.boundaryComboChanged)

    def _applySlot(self):
        self.touched = True
        self.close()

    def _discardSlot(self):
        self.touched = False
        self.close()

    def appendToProject(self):
        """ToDo"""
        return

    def readFromProject(self):
        """ToDo"""
        return
