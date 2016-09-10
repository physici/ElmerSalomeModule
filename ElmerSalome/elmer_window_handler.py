# -*- coding: utf-8 -*-
"""
Created on Sat Sep  3 14:31:15 2016

@author: Rainer Jacob
"""

from PyQt4 import QtGui


import sys
import os

import generalsetup

path = os.path.dirname(os.path.abspath(__file__))
path_forms = path + "\\forms\\"
path_edfs = path + "\\edf\\"

def about():
    QtGui.QMessageBox.about(None, "About ELMER window handler",
                                    "Provides a handler to access ELMER configuration windows.\n" \
                                    "Requires ELMER, ELMERGUI and ELMER_HOME variable to be set.\n\n" \
                                    "Functionality provided only in Mesh-module.")
        
def showGeneralSetup():
    """Initialize an instance of GeneralSetup and returns it to Salome"""
    qwidget = generalsetup.GeneralSetup(path_forms)
    return qwidget


#app = QtGui.QApplication(sys.argv)
#window = showGeneralSetup()
#sys.exit(app.exec_())



