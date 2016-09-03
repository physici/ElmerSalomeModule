# -*- coding: utf-8 -*-
"""
Created on Sat Sep  3 14:31:15 2016

@author: Rainer Jacob
"""

from PyQt4 import QtGui

def about():
    QtGui.QMessageBox.about(None, "About ELMER window handler",
                                    "Provides a handler to access ELMER configuration windows.\n" \
                                    "Requires ELMER to be installed and ELMER_HOME variable to be set.\n\n" \
                                    "Functionality provided only in Mesh-module.")
    



