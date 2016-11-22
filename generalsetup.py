# -*- coding: utf-8 -*-
"""
Created on Sat Sep 10 20:26:27 2016

@author: Rainer Jacob

General setup class
"""

from PyQt4 import QtGui
from PyQt4 import uic


class GeneralSetup(QtGui.QDialog):
    """Class that provides the General setup dialog and its functionality"""

    def __init__(self, path_forms):
        """Constructor of dialog using the uic-loader"""

        # initialize base class
        super(GeneralSetup, self).__init__()
        uic.loadUi(path_forms + "\\generalsetup.ui", self)
        self.acceptButton.clicked.connect(self.applyChanges)

    def applyChanges(self):
        """Apply button hit"""
        QtGui.QMessageBox.about(None, "Test", "Test")
