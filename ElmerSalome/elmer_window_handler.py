# -*- coding: utf-8 -*-
"""
Created on Sat Sep  3 14:31:15 2016

@author: Rainer Jacob
"""

from PyQt4 import QtGui

import os, os.path, sys
import glob
import tempfile

from xml.etree import ElementTree as et


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


def xmlMerge(path):
    """Merges all edf-xml files in the given directory into a temporary file\n
    returns the temporary file object with the cursor at the beginning"""
    
    mybuf = tempfile.TemporaryFile()
    
    xml_files = glob.glob(path + "*.xmls")
    first = None
    for xml_file in xml_files:
        data = et.parse(xml_file).getroot()
        if first is None:
            first = data
        else:
            first.extend(data)

    mybuf.write(et.tostring(first))
    mybuf.seek(0)
    return mybuf

#app = QtGui.QApplication(sys.argv)
#window = showGeneralSetup()
#sys.exit(app.exec_())



