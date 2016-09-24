# -*- coding: utf-8 -*-
"""
Created on Sat Sep  3 14:31:15 2016

@author: Rainer Jacob
"""

from PyQt4 import QtGui
from PyQt4 import QtXml
from PyQt4 import QtCore

import os, os.path
import sys
import glob
import tempfile

from xml.etree import ElementTree as et

import solverparameters
import generalsetup
import dynamiceditor

path = os.path.dirname(os.path.abspath(__file__))
path_forms = path + "\\forms\\"
path_edfs = path + "\\edf\\"

class elmerWindowHanlder():
    
    equationEditor = []
    solverParameterEditor = []
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
        ge = generalsetup.GeneralSetup(path_forms)
        return ge

    def showSolverParametersEditor(self):
        """Initialize an instance of Solver Param Editor and returns it to Salome"""
        sp = solverparameters.SovlerParameterEditor(path_forms)
        return sp
        
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
            """ToDo"""
            return
        
        elif(signal == dynamiceditor.MatTypes.MAT_DELETE):
            """ToDo"""
            return
        
    def editNumericalMethods(self, current, ids):
        """Edit the solver specific properties"""

        title = ""
        for i in range(0, len(self.equationEditor)):
            title = self.equationEditor[i].tabWidget.tabText(current)
            break
        
        if(title == "General"):
            sys.stdout.write("No solver controls for 'General' equation options")
            sys.stdout.flush()
            return
            
        if(current >= len(self.solverParameterEditor)):
            self.solverParameterEditor.append(solverparameters.SovlerParameterEditor(path_forms))

        spe = self.solverParameterEditor[current]
        spe.setWindowTitle("Solver control for {}".format(title))
        spe.solverName = title
        
        if(spe.generalOptions == None):
            spe.generalOptions = dynamiceditor.DynamicEditor()
            spe.generalOptions.setupTabs(self._elmerdefs, "Solver", current)
            spe.solverControlTabs.insertTab(0, spe.generalOptions.tabWidget.widget(current),
                                            "Solver specific options")
        
        for i in range(0, spe.generalOptions.tabWidget.count()):
            if(spe.generalOptions.tabWidget.tabText(i) == title):
                spe.solverControlTabs.insertTab(0, spe.generalOptions.tabWidget.widget(i),
                                            "Solver specific options")       
                break
        
        spe.show()
            
          
    def dynamicEditorNameChange(self, t):
        """ToDo"""
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
        self._elmerdefs.setContent(temp)        
        

#if __name__ == "__main__":
#    sys.path.append(r"C:\opt\SALOME-7.8.0-WIN64\PLUGINS\ElmerSalome")
#    app = QtGui.QApplication(sys.argv)
#    ewh = elmerWindowHanlder()
#    de = ewh.showAddEquation()
#    de.show()
#    #sp = ewh.showSolverParametersEditor()
#    #sp.show()
#    sys.exit(app.exec_())


