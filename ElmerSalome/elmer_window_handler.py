# -*- coding: utf-8 -*-
"""
Created on Sat Sep  3 14:31:15 2016

@author: Rainer Jacob
"""

from PyQt4 import QtGui
from PyQt4 import QtXml

import os, os.path
import sys
import glob
import tempfile

from xml.etree import ElementTree as et


import generalsetup
import dynamiceditor

path = os.path.dirname(os.path.abspath(__file__))
path_forms = path + "\\forms\\"
path_edfs = path + "\\edf\\"

class elmerWindowHanlder():
    
    equationEditor = []
    _elmerdefs = None
    
    def __init__(self):
        self.xmlMerge(path_edfs)        

    def about(self):
        QtGui.QMessageBox.about(None, "About ELMER window handler",
                                        "Provides a handler to access ELMER configuration windows.\n" \
                                        "Requires ELMER, ELMERGUI and ELMER_HOME variable to be set.\n\n" \
                                        "Functionality provided only in Mesh-module.")
        
    def showGeneralSetup(self):
        """Initialize an instance of GeneralSetup and returns it to Salome"""
        qwidget = generalsetup.GeneralSetup(path_forms)
        return qwidget
        
    def showAddEquation(self):
        """Creates a new instance of the dynamic editor for adding an equation"""
        de = dynamiceditor.DynamicEditor()
        self.equationEditor.append(de)
        current = len(self.equationEditor) - 1
        de.setupTabs(self._elmerdefs, "Equation", current)
        
        de.applyButton.setText("Add")
        de.discardButton.setText("Cancel")
    
        de.dynamicEditorReady[int, int].connect(self.pdeEditorFinishedSlot)    
        
        de.spareButton.setText("Edit Solver Settings")
        de.spareButton.show()
        de.dynamicEditorSpareButtonClicked[int, int].connect(self.editNumericalMethods)
        
        de.nameEdit.textChanged.connect(self.dynamicEditorNameChange)
        
        #todo add menu entry in salome
        equationName = de.nameEdit.text().trimmed()
        
        return de, equationName
        
    def pdeEditorFinishedSlot(self, signal, ids):
        de = self.equationEditor[ids]
        equationName = de.nameEdit.text().trimmed()
        signalOK = False
        if(signal == dynamiceditor.MatTypes.MAT_OK or
            signal == dynamiceditor.MatTypes.MAT_APPLY):
            signalOK = True

        if(equationName.isEmpty() and signalOK):
            sys.stdout.write("No equation name\n")
            sys.stdout.flush()
            return
        
        if(signalOK):
            if(de.menuAction != None):
                de.menuAction = equationName
                sys.stdout.write("Update\n")
                sys.stdout.flush()
                if(signal == dynamiceditor.MatTypes.MAT_OK):
                    de.close()
                    
        elif(signal == dynamiceditor.MatTypes.MAT_NEW):
            #still todo
            return
        
        elif(signal == dynamiceditor.MatTypes.MAT_DELETE):
            #still todo
            return
        
    def editNumericalMethods(self, current, ids):
        #still todo
        return
    
    def dynamicEditorNameChange(self, t):
        #still todo
        return
               
    def xmlMerge(self, path):
        """Merges all edf-xml files in the given directory into a temporary file\n
        returns the temporary file object with the cursor at the beginning"""
        
        mybuf = tempfile.TemporaryFile()
    
        gen_file = path + "edf.xml"
        
        first = et.parse(gen_file).getroot()    
        
        xml_files = glob.glob(path + "*.xml")
        xml_files = [file for file in xml_files if not os.path.basename(file).startswith("edf")]
    
        for xml_file in xml_files:
            data = et.parse(xml_file).getroot()
            first.extend(data)
        
        mybuf.write(et.tostring(first))
        mybuf.seek(0)
        temp = mybuf.read().decode()
        mybuf.close()
        
        self._elmerdefs = QtXml.QDomDocument()    
        self._elmerdefs.setContent(temp.decode())        
        

#if __name__ == "__main__":
#    sys.path.append(r"C:\opt\SALOME-7.8.0-WIN64\PLUGINS\ElmerSalome")
#    app = QtGui.QApplication(sys.argv)
#    elmerdefs = QtXml.QDomDocument()    
#    elmerdefs.setContent(a.decode())
#    de.show()
#    sys.exit(app.exec_())


