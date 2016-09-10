# -*- coding: utf-8 -*-
"""
Created on Sat Sep 10 21:20:24 2016

@author: Rainer Jacob

Dynamic editor class

Class changes appaerance according to provide edf-xml document
"""

from PyQt4 import QtGui
from PyQt4 import QtXml
from PyQt4 import QtCore

class DynamicEditor(QtGui.QWidget):
    
    def setupTabs(elmerDefs: QtXml.QDomDocument, section: str, ID: int, self):
        """Creates the taps of the dynamic widget according to the elmerDefs"""
        self.ID = ID

        #get root element
        root = elmerDefs.documentElement()
        
        tabWidget = QtGui.QTableWidget()
        tabWidget.setUsesScrollButtons(True)
        tabWidget.setElideMode(QtCore.Qt.ElideNone)
        
        all_stuff = root.firstChildElement("ALL")
        element = root.firstChildElement("PDE")
        
        tabs = 0
        
        
        
                
        
        
