from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

import nodz.nodz_utils as utils
from extensions.customWidgets import CentredCellCheckbox, UniqueNameTable

import os

class ToolkitUI(QtWidgets.QWidget):
    def __init__(self, parent):
        super(ToolkitUI, self).__init__()
        self.parent = parent
        self.resize(800, 300)
        self.setWindowIcon(self.style().standardIcon(getattr(QtWidgets.QStyle,"SP_TitleBarMenuButton")))
        self.setWindowTitle("Toolkit Manager")
        
        # Array of names and dict of paths
        self.toolkitNames = []
        self.toolkitPaths = {}

        self.buildUI()
        self.setLayout(self.layout)
        
    def buildUI(self):
        self.layout = QtWidgets.QHBoxLayout()
        
        # Build the table
        self.toolkitTable = QtWidgets.QTableWidget()
        self.toolkitTable.setColumnCount(3)
        header = self.toolkitTable.horizontalHeader()
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.toolkitTable.verticalHeader().setVisible(False)
        self.toolkitTable.setHorizontalHeaderLabels(["Name", "Display", "Path"])
        self.toolkitTable.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.layout.addWidget(self.toolkitTable)
        
        # Build the buttons
        self.buttonLayout = QtWidgets.QVBoxLayout()
        self.btAdd = QtWidgets.QPushButton("Add Toolkit")
        self.btAdd.clicked.connect(self.loadToolkit)
        self.btRemove = QtWidgets.QPushButton("Remove Toolkit")
        self.btRemove.clicked.connect(self.deleteRow)
        #self.btOpen = QtWidgets.QPushButton("Open Toolkit Folder")
        vspace = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        
        self.buttonLayout.addWidget(self.btAdd)
        self.buttonLayout.addWidget(self.btRemove)
       # self.buttonLayout.addWidget(self.btOpen)
        self.buttonLayout.addItem(vspace)
        
        self.layout.addItem(self.buttonLayout)
        
    # Show prompt to load toolkit and add to table
    def loadToolkit(self):
        path = os.path.normpath(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        if (path is not ''):
            if os.path.exists(os.path.normpath(path + "/config.json")):
                name = os.path.basename(os.path.normpath(path))
                
                # Check if theres a matching name or path in the table
                for row in range(self.toolkitTable.rowCount()):
                    if self.toolkitTable.item(row, 0).text() == name:
                        QtWidgets.QMessageBox.warning(self, "Warning", "Toolkit with matching name already exists")
                        return
                    
                    if self.toolkitTable.item(row, 2).text() == path:
                        QtWidgets.QMessageBox.warning(self, "Warning", "Toolkit with matching path already exists")
                        return 
            
                self.addRow(name, path)
                self.reloadToolkits()
            else:
                QtWidgets.QMessageBox.warning(self, "Warning", "Cannot find config file in selected folder")
        
    # Generates a row from a given toolkit name and path
    def addRow(self, toolkitName, toolkitPath, toolkitShow = True):
        row = self.toolkitTable.rowCount()
        self.toolkitTable.insertRow(row)
        
        name = QtWidgets.QTableWidgetItem(toolkitName)
        name.setFlags(QtCore.Qt.ItemIsEnabled)
        
        show = CentredCellCheckbox()
        show.setChecked(toolkitShow)
        show.connect(self.reloadToolkits)
        
        path = QtWidgets.QTableWidgetItem(toolkitPath)
        path.setFlags(QtCore.Qt.ItemIsEnabled)
        
        self.toolkitTable.setItem(row, 0, name)
        self.toolkitTable.setCellWidget(row, 1, show)
        self.toolkitTable.setItem(row, 2, path)
        
    # Deletes the currently selected row
    def deleteRow(self):
        row = self.toolkitTable.currentRow()  
        toolkit = self.toolkitTable.item(row, 0).text()
        if self.parent.reloadConfig(toolkit, False):
            self.toolkitTable.removeRow(row)
            self.reloadToolkits()
        
    # If a settings json exists, loads it and sets up the table
    def loadToolkitSettings(self):
        tks = utils._loadData(os.path.normpath("./toolkits/toolkitConfig.json"))
        for tk in tks:
            self.addRow(tks[tk]["name"], tks[tk]["path"], tks[tk]["show"])
            
        self.reloadToolkits()
            
        
    # Generates the initial json file based on the toolkits available in the WARIO root folder
    def genSettings(self):
        for root, directories, files in os.walk(os.path.normpath('./toolkits')):
            for dir in directories:
                if dir != "__pycache__":
                    self.addRow(dir, os.path.normpath("./toolkits/" + dir))
            break
                
        self.reloadToolkits()
        
    # Makes sure that the toolkits for loaded files exist and are shown
    def checkAdded(self, toolkit):
        
        if toolkit == "custom":
            return True
        
        for row in range(self.toolkitTable.rowCount()):
            if self.toolkitTable.item(row, 0).text() == toolkit:
                self.parent.reloadConfig(toolkit, True)
                self.toolkitTable.cellWidget(row, 1).setChecked(True)
                return True
        
        QtWidgets.QMessageBox.warning(self, "Warning", "Unable to load file due to missing toolkit: {0}. Please add this toolkit via the toolkit manager to continue".format(toolkit))
        return False
        
    # Updates the WARIO UI to make sure that the correct rows are showing and save the list
    def reloadToolkits(self):
        self.toolkitNames = []
        data = {}

        # Gather the toolkits that are marked to show
        for row in range(self.toolkitTable.rowCount()):
            name = self.toolkitTable.item(row, 0).text()
            if self.toolkitTable.cellWidget(row, 1).isChecked():
                self.toolkitNames.append(name)
                self.toolkitPaths[name] = self.toolkitTable.item(row, 2).text()
            else:
                # If its not checked but still in use, re-check it which calls this class again
                if self.parent.checkToolkitInUse(name):
                    self.parent.reloadConfig(name, True)
                    self.toolkitTable.cellWidget(row, 1).setChecked(True)
                    return
                else:
                    self.parent.reloadConfig(name, False)

            # Gather the required save data
            show = self.toolkitTable.cellWidget(row, 1).isChecked()
            path = os.path.normpath(self.toolkitTable.item(row, 2).text())
            data[name] = {"name" : name, "show" : show, "path" : path}
        
        # Update the base UI
        self.parent.parent.buildToolkitToggles()
        self.parent.helpUI.buildToolkitHelp(self.toolkitNames)
        
        # Save the config file
        utils._saveData(filePath=os.path.normpath("./toolkits/toolkitConfig.json"), data=data)
        
    