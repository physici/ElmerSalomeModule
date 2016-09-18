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


class MatTypes():
    """Enumeration class for signals"""
    MAT_APPLY = 1
    MAT_OK = 2
    MAT_NEW = 3
    MAT_DELETE = 4


class hash_entry_t():
    """Seems to be a container for exchanging stuff"""
    widget = None
    label = None
    elem = None
    
class DynLineEdit(QtGui.QWidget):

    def __init__(self):
        """Constructor"""
        super(DynLineEdit, self).__init__()
        self.name = ""
        self.label = None
        self.frame  = None
        self.layout = None
        self.textEdit = None
        self.closeButton = None 
        self.lineEdit = QtGui.QLineEdit()
    
    
    def editSlot(self):
        q = self.lineEdit
        s = q.text()
        
        if(self.frame):
            self.frame.show()
            self.frame.raise_()
            return
        
        self.textEdit = QtGui.QTextEdit()
        self.textEdit.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        
        s.replace(";", "\n")
        self.textEdit.append(s)
        
        self.closeButton = QtGui.QPushButton("&Close")
        self.closeButton.clicked.connect(self.lineEditClose)
        
        self.label = QtGui.QLabel()
        self.label.setText(self.name)
        
        self.layout = QtGui.QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.textEdit)
        self.layout.addWidget(self.closeButton)
        
        self.frame = QtGui.QFrame()
        self.frame.setLayout(self.layout)
        self.frame.show()
        self.frame.setWindowTitle(self.name)
    
    def lineEditClose(self):
          q = self.textEdit.toPlainText()
          q.replace( '\n', ';' )
          
          self.lineEdit.setText(q)
          self.frame.close()
          self.name = ""
          self.label = None
          self.textEdit = None          
          self.closeButton = None
          self.layout = None
          self.frame = None



class DynamicEditor(QtGui.QWidget):
    """DynamicEditor base class"""

    #signals
    dynamicEditorSpareButtonClicked = QtCore.pyqtSignal(int, int,
                                                        name = "dynamicEditorSpareButtonClicked")
    dynamicEditorReady = QtCore.pyqtSignal(int, int,
                                           name = "dynamicEditorReady")

       
    def __init__(self):
        """Constructor"""
        super(DynamicEditor, self).__init__()
        
        #public
        self.menuAction = None
        self.ID = -1
        self.touched = False
        
        self.okButton = None
        self.newButton = None
        self.applyButton = None
        self.spareButton = None
        self.discardButton = None
        
        self.h = hash_entry_t()
        self.qhash = {}

        self.tabWidget = None
        self.nameEdit = None
        self.tabs = None
        
        self.spareBox = None
        self.spareScroll = None
                
        #private
        self._root = None
        self._all_stuff = None
        self._element = None
        self._name = None
        self._section = None
        self._param = None
     

   
    def setupTabs(self, elmerDefs , Section, ID):
        """Creates the taps of the dynamic widget according to the elmerDefs"""
        self.ID = ID

        layout = self.layout()
        if(layout != None):
            item = layout.takeAt(0)
            while(item != 0):
                item = None
                if(self.tabWidget != None):
                    self.tabWidget.clear()
                    self.tabWidget = None
                item = layout.takeAt(0)
            self.layout = None

        #get root element
        self._root = elmerDefs.documentElement()
        
        self.tabWidget = QtGui.QTabWidget()
        self.tabWidget.setUsesScrollButtons(True)
        self.tabWidget.setElideMode(QtCore.Qt.ElideNone)
        
        self._all_stuff = self._root.firstChildElement("ALL")
        self._element = self._root.firstChildElement("PDE")
        
        self.tabs = 0
        
        while(self._element.isNull() == False):
            self._name = self._element.firstChildElement("Name")
            grid = QtGui.QGridLayout()
            params = 0
            for x in range(0,2):
                if(x == 0):
                    if(self._name.text().trimmed() == "General"):
                        continue
                    self._section = self._all_stuff.firstChildElement(Section)
                else:
                    self._section = self._element.firstChildElement(Section)
            
                self._param = self._section.firstChildElement("Parameter")  
                      
                while(self._param.isNull() == False):
                    
                    #label
                    widget_type = self._param.attribute("Widget","Edit");
                    widget_enabled = self._param.attribute("Enabled","True");
                    widget_visible = self._param.attribute("Visible","True");
                    paramType = self._param.firstChildElement("Type").text().trimmed();
                    labelName = self._param.firstChildElement("Name").text().trimmed();
                    sifName   = self._param.firstChildElement("SifName").text().trimmed();
                    if(sifName == ""):
                        sifName = labelName
                    paramDefault = self._param.firstChildElement("DefaultValue").text().trimmed();
                    whatis = self._param.firstChildElement("Whatis").text().trimmed();
                    statusTip = self._param.firstChildElement("StatusTip").text().trimmed();
                    fullName  = "/" + self._name.text().trimmed() + "/" 
                    fullName = fullName + Section + "/" + labelName + "/" + str(ID);
                    self.h.widget = None;
                    
                    if(widget_type == "Edit"):
                        edit = DynLineEdit()
                        self.h.widget = edit.lineEdit
                        edit.lineEdit.setText(paramDefault)
                        edit.name = fullName
                        edit.lineEdit.returnPressed.connect(edit.editSlot)
                        edit.lineEdit.textChanged.connect(self.textChangedSlot)
                    
                    elif(widget_type == "TextEdit"):
                        textEdit = QtGui.QTextEdit()
                        currentFont = textEdit.currentFont()
                        fontMetrics = QtGui.QFontMetrics(currentFont)
                        fontHeight = fontMetrics.height()
                        textEdit.setMinimumHeight(5*fontHeight)
                        textEdit.setMaximumHeight(8*fontHeight)
                        self.h.widget = textEdit
                    
                    elif(widget_type == "Combo"):
                        combo = QtGui.QComboBox()
                        self.h.widget = combo;
                        count = 0
                        active=0
                        item = self._param.firstChildElement("Item")
                        while (item.isNull() == False):
                            itemType = item.attribute("Type", "")
                            if(itemType == "Active"):
                                active = count
                            itemName = item.firstChildElement("Name")
                            count += 1
                            combo.insertItem(count,itemName.text().trimmed())
                            item = item.nextSiblingElement("Item")  
                        combo.setCurrentIndex(active)
                        combo.currentIndexChanged.connect(self.comboSlot)
                    
                    elif(widget_type == "CheckBox"):
                        l = QtGui.QCheckBox()
                        self.h.widget = l
                        l.setText("")
                        l.setChecked(False)
                        if(paramDefault == "True"):
                            l.setChecked(True)
                        l.stateChanged.connect(self.lSlot)
                    
                    elif(widget_type == "Label"):
                        label = QtGui.QLabel()
                        font = QtGui.QFont()
                        font.setBold(True)
                        font.setUnderline(True)
                        label.setFont(font)
                        label.setText(labelName)
                        self.h.widget = label
                    
                    if(self.h.widget):
                        self.h.widget.setWhatsThis(whatis)
                        self.h.widget.setStatusTip(statusTip)
                        self.h.widget.setProperty("dom address",fullName)
                        self.h.elem = self._param
                        if(widget_enabled == "False"):
                            self.h.widget.setEnabled(False)
                        if(widget_type != "TextEdit"):
                            self.h.widget.setFixedHeight(18)
                        if(widget_type == "TextEdit"):
                            textEditLabel = QtGui.QLabel()
                            textEditLabel.setText(labelName)
                            self.h.label = textEditLabel
                            grid.addWidget(self.h.widget, params, 0, 1, 2);
                        
                            if(widget_visible == "False"):
                                self.h.label.hide()
                                self.h.widget.hide()
                      
                        elif(widget_type != "Label"):
                            label = QtGui.QLabel()
                            label.setText(labelName)
                            self.h.label = label
                            grid.addWidget(self.h.label,  params, 0)
                            grid.addWidget(self.h.widget, params, 1)
                        
                            if(widget_visible == "False"):
                                self.h.label.hide()
                                self.h.widget.hide()
                        else:
                            self.h.label = None
                            grid.addWidget(self.h.widget, params, 0)
                        self.qhash[fullName] = self.h
                                                         
                    self._param = self._param.nextSiblingElement("Parameter")
                    params += 1
        
            dummyWidget = QtGui.QWidget()
            grid.addWidget(dummyWidget, params, 0)
            grid.setRowStretch(params, 1)
    
            frmWidget = QtGui.QWidget()
            frmWidget.setLayout(grid)
    
            src = QtGui.QScrollArea()
            src.setWidget(frmWidget)
            src.setMinimumHeight(300)
            src.setWidgetResizable(True)
            
            if(params > 0):
                self.tabWidget.addTab(src, self._name.text().trimmed())
            
            self.tabs += 1
            self._element = self._element.nextSiblingElement("PDE")
        
        #Buttons:
        lbl = QtGui.QLabel()
        lbl.setText("Name:")
        self.nameEdit  = QtGui.QLineEdit()
        self.nameEdit.setText(Section + " " + str(ID+1))

        self.applyButton = QtGui.QPushButton("&Add")
        #applyButton.setIcon(addIcon)
        self.applyButton.clicked.connect(self.applyButtonClicked)
        
        self.discardButton = QtGui.QPushButton("&Remove")
        #discardButton.setIcon(removeIcon)
        self.discardButton.clicked.connect(self.discardButtonClicked)
        
        self.okButton = QtGui.QPushButton("&OK")
        #okButton.setIcon(okIcon)
        self.okButton.clicked.connect(self.okButtonClicked)

        self.newButton = QtGui.QPushButton("&New")
        #self.newButton.setIcon(newIcon)
        self.newButton.clicked.connect(self.newButtonClicked)

        nameLayout = QtGui.QHBoxLayout()
        nameLayout.addWidget(lbl)
        nameLayout.addWidget(self.nameEdit)

        buttonLayout = QtGui.QHBoxLayout()
        buttonLayout.addWidget(self.newButton)
        buttonLayout.addWidget(self.applyButton)
        buttonLayout.addWidget(self.okButton)
        buttonLayout.addWidget(self.discardButton)

        spareButtonLayout = QtGui.QHBoxLayout()
        self.spareButton = QtGui.QPushButton("SpareButton")
        self.spareButton.setVisible(False)
        spareButtonLayout.addWidget(self.spareButton)
        self.spareButton.clicked.connect(self.spareButtonClicked)

        self.spareScroll = QtGui.QScrollArea()
        self.spareScroll.hide()

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.tabWidget)
        mainLayout.addWidget(self.spareScroll)
        mainLayout.addLayout(spareButtonLayout)
        mainLayout.addLayout(nameLayout)
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)
        
        self.setWindowTitle(Section)
        
    def lSlot(self, state):
        """Event when CheckBox changed"""
        self._param = QtXml.QDomElement()
        q = QtGui.QObject.sender().property("dom address").toString()
    
        ind = int(q.lastIndexOf( '/', -1))
        ids = str(q.mid(ind,-1))
    
        self._param = self.qhash[q].elem.firstChildElement("Activate")
        while(self._param.isNull() != False):
            q = self._param.text().trimmed() + ids
            self.qhash[q].widget.setEnabled(state)
            widget_visible = self.qhash[q].elem.attribute("Visible","Unknown")
            if(state == False & widget_visible != "Unknown"):
                self.qhash[q].label.hide()
                self.qhash[q].widget.hide()
            else:
              self.qhash[q].label.show()
              self.qhash[q].widget.show()
            self._param = self._param.nextSiblingElement("Activate")
    
        self._param = self.qhash[q].elem.firstChildElement("Deactivate")
        while(self._param.isNull() != False):
             q = self._param.text().trimmed() + ids
             self.qhash[q].widget.setEnabled(-state)
             widget_visible = self.qhash[q].elem.attribute("Visible","Unknown")
             if(state == True & widget_visible != "Unknown" ):
                 self.qhash[q].label.hide()
                 self.qhash[q].widget.hide()
             else:
                 self.qhash[q].label.show()
                 self.qhash[q].widget.show()
        self._param = self._param.nextSiblingElement("Deactivate")

    def textChangedSlot(self, text):
        """Event when TextBox changed"""
        self._param = QtXml.QDomElement()
        q = QtGui.QObject.sender().property("dom address").toString()
        
        ind = int(q.lastIndexOf( '/', -1))
        ids = str(q.mid(ind,-1))
    
        self._param = self.qhash[q].elem.firstChildElement("Activate");
        while(self._param.isNull() != False):
            q = self._param.text().trimmed() + ids
            widget_visible = self.qhash[q].elem.attribute("Visible","Uknown")
        
            if(text != ""):
                self.qhash[q].widget.setEnabled(True)
                self.qhash[q].widget.show()
                self.qhash[q].label.show()
            else:
                self.qhash[q].widget.setEnabled(False)
                if(widget_visible != "Unknown"):
                    self.qhash[q].label.hide()
                    self.qhash[q].widget.hide()
            self._param = self._param.nextSiblingElement("Activate")
    
    def comboSlot(self, select):
        """Event when comboBox changend"""
        q = QtGui.QObject.sender().property("dom address").toString()
        item = QtXml.QDomElement()
        
        ind = int(q.lastIndexOf( '/', -1))
        ids= str(q.mid(ind,-1))
        
        item = self.qhash[q].elem.firstChildElement("Item")
        while(item.isNull() != False):
            itemName = item.firstChildElement("Name")
            if(itemName.text().trimmed() != select):
                activ = item.firstChildElement("Activate")
                while(activ.isNull() != False):
                    activ=activ.nextSiblingElement("Activate")
                    s=activ.text().trimmed() + ids
                    self.h = self.qhash[s]
                    widget_enabled = self.h.elem.attribute("Enabled","True")
                    widget_visible = self.h.elem.attribute("Visible","Unknown")
        
                    self.h.widget.setEnabled(False)
                    if(widget_visible != "Unknown"):
                        self.h.label.hide()
                        self.h.widget.hide()
                    item = item.nextSiblingElement("Item")
        
        item = self.qhash[q].elem.firstChildElement("Item")
        while(item.isNull() != False):
            itemName = item.firstChildElement("Name")
            if(itemName.text().trimmed() == select ):
                activ = item.firstChildElement("Activate")
                while(activ.isNull() != False):
                    s = activ.text().trimmed() + ids
                    self.h = self.qhash[s]
                    self.h.widget.setEnabled(True)
                    self.h.label.show()
                    self.h.widget.show()
                    activ = activ.nextSiblingElement("Activate")
                item = item.nextSiblingElement("Item")
                
    def minimumSizeHint(self):
        return QtCore.QSize(128, 128)

    def sizeHine(self):
        return QtCore.QSize(400, 500)
    
    def spareButtonClicked(self):
        self.dynamicEditorSpareButtonClicked.emit(self.tabWidget.currentIndex, self.ID)
    
    def applyButtonClicked(self):
        self.touched = True
        self.dynamicEditorReady.emit(MatTypes.MAT_APPLY, self.ID)
    
    def discardButtonClicked(self):
        self.touched = False
        self.dynamicEditorReady.emit(MatTypes.MAT_DELETE, self.ID) 
        
    def okButtonClicked(self):
        self.touched = False
        self.dynamicEditorReady.emit(MatTypes.MAT_OK, self.ID)
        
    def newButtonClicked(self):
        self.touched = False
        self.dynamicEditorReady.emit(MatTypes.MAT_NEW, self.ID)
        
    def dumpHash(self, projectDoc, item):
        for j in range(0, self.qhash.count()):
            key = self.qhash.keys()[j]
            value = self.qhash.values()[j]
            elem = value.elem
            widget = value.widget
    
            itemWidget = projectDoc.createElement("widget")
            item.appendChild(itemWidget)
            
            itemKey = projectDoc.createElement("key")
            itemKeyValue = projectDoc.createTextNode(key)
            itemKey.appendChild(itemKeyValue)
            itemWidget.appendChild(itemKey)
    
            if(elem.attribute("Widget") == "CheckBox"):
                checkBox = widget
                itemCheckBox = projectDoc.createElement("value")
                itemCheckBoxValue = projectDoc.createTextNode(int(checkBox.isChecked))
                itemCheckBox.appendChild(itemCheckBoxValue)
                itemWidget.appendChild(itemCheckBox)
                itemWidget.setAttribute("type", "CheckBox")
      
            elif(elem.attribute("Widget") == "Edit"):
                lineEdit = widget
                itemLineEdit = projectDoc.createElement("value")
                itemLineEditValue = projectDoc.createTextNode(lineEdit.text().trimmed())
                itemLineEdit.appendChild(itemLineEditValue)
                itemWidget.appendChild(itemLineEdit)
                itemWidget.setAttribute("type", "Edit")

            elif(elem.attribute("Widget") == "TextEdit"):
                textEdit = widget
                itemTextEdit = projectDoc.createElement("value")
                itemTextEditValue = projectDoc.createTextNode(textEdit.toPlainText())
                itemTextEdit.appendChild(itemTextEditValue)
                itemWidget.appendChild(itemTextEdit)
                itemWidget.setAttribute("type", "TextEdit")
      
            elif(elem.attribute("Widget") == "Combo"):
                comboBox = widget
                itemComboBox = projectDoc.createElement("value")
                itemComboBoxValue = projectDoc.createTextNode(comboBox.currentText().trimmed())
                itemComboBox.appendChild(itemComboBoxValue)
                itemWidget.appendChild(itemComboBox)
                itemWidget.setAttribute("type", "Combo")
      
            elif(elem.attribute("Widget") == "Label"):
                label = widget
                itemLabel = projectDoc.createElement("value")
                itemLabelValue = projectDoc.createTextNode(label.text().trimmed())
                itemLabel.appendChild(itemLabelValue)
                itemWidget.appendChild(itemLabel)
                itemWidget.setAttribute("type", "Label")
                
    def populateHash(self, item):
        widget = item.firstChildElement("widget")
        
        while(widget.isNull() != False):
            qtype = widget.attribute("type").trimmed()
            key = widget.firstChildElement("key").text().trimmed()
            value = widget.firstChildElement("value").text().trimmed()
            
            if(value.isEmpty()):
                continue
            
            splittedKey = key.split("/")
    
            #Compare with current hash:
            match_found = False
            for j in range(0, self.qhash.count()):
                hashkey = self.qhash.keys()[j]
                splittedHashKey = hashkey.split("/");
                hashvalue = self.qhash.values()[j]
                widget = hashvalue.widget
                elem = hashvalue.elem
      
                if((splittedKey[1] == splittedHashKey[1]) &
                (splittedKey[2] == splittedHashKey[2]) &
                (splittedKey[3] == splittedHashKey[3])):
                    match_found = True
	
                    if(elem.attribute("Widget") == "CheckBox"):
                        if(qtype != "CheckBox"):
                            print("Load project: type mismatch with checkBox")
                        checkBox = widget
                        if(value.toInt() == 1):
                            checkBox.setChecked(True)
                        else:
                            checkBox.setChecked(False)
	  
                    elif(elem.attribute("Widget") == "Edit"): 
                        if(qtype != "Edit"):
                            print("Load project: type mismatch with Edit")
                        lineEdit = widget
                        lineEdit.setText(value)
                    
                    elif(elem.attribute("Widget") == "TextEdit"):
                        if(qtype != "TextEdit"):
                            print("Load project: type mismatch with TextEdit")
                        textEdit = widget
                        textEdit.clear()
                        textEdit.append(value)
                        
                    elif(elem.attribute("Widget") == "Combo"):
                        if(qtype != "Combo"):
                            print("Load project: type mismatch with Combo")                        
                        comboBox = widget
                        for k in range (0, comboBox.count()):
                            current = comboBox.itemText(k).trimmed()
                            if(current == value.trimmed()):
                                comboBox.setCurrentIndex(k);
	  
            if(match_found == False):
                print("Error: Unable to set menu entry: key: " + key.toAscii().data())
        widget = widget.nextSiblingElement("widget")
        