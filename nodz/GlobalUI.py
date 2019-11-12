from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import uic
import nodz.nodz_utils as utils
from nodz.customWidgets import *
from nodz.globalWidgets import *

# Global variable UI
class GlobalUI(QtWidgets.QWidget):
    def __init__(self, parent):
        super(GlobalUI, self).__init__()        
        self.layout = QtWidgets.QVBoxLayout()
        self.vars = []
        self.parent = parent
        
        self.buildUI()
        self.setLayout(self.layout)
        self.resize(700, 300)
        self.setWindowIcon(self.style().standardIcon(getattr(QtWidgets.QStyle,"SP_TitleBarMenuButton")))
        self.setWindowTitle("Global Settings")
        
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.installEventFilter(self)
        
    def buildUI(self):
    
        self.table = UniqueNameTable()
        self.table.setColumnCount(4)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.table.setHorizontalHeaderLabels(['Variable Name', 'Type', 'Value', 'Constant'])
        self.table.verticalHeader().setVisible(False)
        self.layout.addWidget(self.table)
        
        buttonLayout = QtWidgets.QHBoxLayout()
        self.btAdd = QtWidgets.QPushButton(text = "Add")
        self.btAdd.clicked.connect(self.addRow)
        buttonLayout.addWidget(self.btAdd)
        
        self.btRemove = QtWidgets.QPushButton(text = "Remove")
        self.btRemove.clicked.connect(self.removeRow)
        buttonLayout.addWidget(self.btRemove)
        
        spacer = QtWidgets.QSpacerItem(100, 10, QtWidgets.QSizePolicy.Expanding)
        buttonLayout.addItem(spacer)
        
        self.layout.addLayout(buttonLayout)
        
    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.Close:
            self.genGlobals()
            event.accept()
        elif event.type() == QtCore.QEvent.WindowDeactivate:
            self.genGlobals()
            event.accept()
 
        return False
        
    def genGlobals(self):
        globals = {}
        self.vars = {}
        
        for row in range(0, self.table.rowCount()):
            gb = {}
            
            widget = self.table.cellWidget(row, 2)
            name = self.table.item(row, 0).text()
            type = self.table.cellWidget(row, 1).currentText()
            value = widget.getData()
            const = True if self.table.item(row, 3).checkState() == QtCore.Qt.Checked else False
            
            gb["file"] = widget.file
            gb["class"] = widget.cls
            gb["type"] = type
            gb["value"] = value
            gb["const"] = const
            widget.saveProperties(gb)
            globals[name] = gb
            
            self.vars[name] = type
            
        self.parent.updateGlobals(globals)
            
        return globals
        
    def loadGlobals(self, globals):
        self.clearTable()
        for gb in globals:
            self.addRow(globals[gb])
            row = self.table.rowCount() - 1
            
            self.table.item(row, 0).setText(gb)
            
            # Use the type of the global to work out which index to load
            id = self.table.cellWidget(row, 1).findText(globals[gb]["type"])
            if id == -1:
                self.table.cellWidget(row, 1).setCurrentIndex(len(self.table.cellWidget(row, 1).items) - 1)
                self.table.cellWidget(row, 1).setCurrentText(globals[gb]["type"])
            else:
                self.table.cellWidget(row, 1).setCurrentIndex(id)
                
            self.table.cellWidget(row, 2).setData(globals[gb])    
            
            if globals[gb]["const"]:
                self.table.item(row, 3).setCheckState(QtCore.Qt.Checked)
            else:
                self.table.item(row, 3).setCheckState(QtCore.Qt.Unchecked)
                
    def genNewRowWidget(self, gb):
        if gb is None:
            return GlobalFileSelect()#GlobalTextbox()
        
        if "file" not in gb.keys():
            return GlobalTextbox()

        module = importlib.import_module(gb["file"])
        cls = getattr(module, gb["class"])
        
        widget = cls()
        widget.setData(gb)
        
        return widget

    def addRow(self, gb = None, name = None):
    
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        if name is None:
            name = "Var{0}".format(self.table.varNameCounter)
            self.table.varNameCounter += 1
        
        # Fixes an error when addRow is called by the button
        if isinstance(gb, bool):
            gb = None
        
        text = QtWidgets.QTableWidgetItem(name)
        value = self.genNewRowWidget(gb)
        
        # Defined in nodz/globalWidgets.py
        combobox = TypeComboBox()
        
        checkbox = QtWidgets.QTableWidgetItem()
        checkbox.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        checkbox.setCheckState(QtCore.Qt.Unchecked)
        
        self.table.setItem(row, 0, text)    
        self.table.setCellWidget(row, 1, combobox)
        self.table.setCellWidget(row, 2, value)
        self.table.setItem(row, 3, checkbox)
        
    def addAutoRow(self, name, gb):
        
        # If the variable already exists then make it unremoveable
        if name in self.table.prevNames.values():
            for i in range(0, self.table.rowCount()):
                if self.table.item(i,0).text() == name:
                    self.table.item(i,0).setFlags(QtCore.Qt.NoItemFlags)
                    self.table.cellWidget(i,1).setCurrentText(gb["type"])
                    self.table.cellWidget(i,1).setEnabled(False)
                    self.table.item(i,3).setFlags(QtCore.Qt.NoItemFlags)
            return
        
        self.addRow(gb, name)
        row = self.table.rowCount() - 1
        
        self.table.item(row,0).setFlags(QtCore.Qt.NoItemFlags)
        self.table.cellWidget(row,1).setCurrentText(gb["type"])
        self.table.cellWidget(row,1).setEnabled(False)
        self.table.item(row,3).setFlags(QtCore.Qt.NoItemFlags)
        
        if gb["const"]:
            self.table.item(row,3).setCheckState(QtCore.Qt.Checked)
        else:
            self.table.item(row,3).setCheckState(QtCore.Qt.Unchecked)
        
        
        self.genGlobals()

    def removeRow(self):
        if self.table.currentRow() != -1:
            # check if the row is editable (i.e. not a toolbox global)
            if self.table.item(self.table.currentRow(), 0).flags() & ~QtCore.Qt.ItemIsEnabled:
                self.table.removeRow(self.table.currentRow())
                self.table.updateNames()
                
    def setRowsEditable(self):
        for row in range(0, self.table.rowCount()):
            self.table.item(row,0).setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
            self.table.cellWidget(row,1).setEnabled(True)
            self.table.item(row,3).setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            
    def clearTable(self):
        while self.table.rowCount() > 0:
            self.table.removeRow(0)
            