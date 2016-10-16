# -*- coding: utf-8 -*-
"""
Created on Sun Oct 16 15:53:26 2016

@author: Rainer Jacob

Widget that allows setting of body properties
"""

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import uic

import elmer_window_handler


class BodyPropertyEditor(QtCore.QtDialog):
    
    def __init__(self, path_forms):
        """Constructor"""
        super(BodyPropertyEditor, self).__init__()
    
        uic.loadUi(path_forms + "bodypropertyeditor.ui", self)
        
        self.material = None
        self.initial = None
        self.force = None
        self.equation = None
        self.touched = False
        
        #signals
        self.applyButton.clicked.connect(self._applySlot)
        self.discardButton.clicked.connect(self._discardSlot)
        self.materialCombo.currentIndexChanged.connect(self.materialComboChanged)
        self.initialConditionCombo.currentIndexChanged.connect(self.initialConditionCombo)        
        self.bodyForceCombo.currentIndexChanged.connect(self.bodyForceCombo)        
        self.equationCombo.currentIndexChanged.connect(self.equationCombo)  
        
    def _applySlot(self):
        self.touched = True
        self.close()
        
    def _discardSlot(self):
        self.touched = False
        self.close()
        
    def materialComboChanged(self, select):
        """ToDo"""
        return
        
    def initialComboChanged(self, select):
        """ToDo"""
        return
        
    def forceComboChanged(self, select):
        """ToDo"""
        return
        
    def equationComboChanged(self, select):
        """ToDo"""
        return
        
    def appendToProject(self):
        """ToDo"""        
        return
    
    def readFromProject(self):
        """ToDo"""
        return
        
    
        
        
        

