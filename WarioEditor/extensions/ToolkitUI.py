from PyQt5 import QtWidgets
from PyQt5 import QtCore

import WarioEditor.nodz.nodz_utils as utils
from wario.CustomWidgets import CentredCellCheckbox, UniqueNameTable

import os

# UI for modifying toolkits, as well as holding toolkit specific info
class ToolkitUI(QtWidgets.QWidget):
    def __init__(self, parent):
        super(ToolkitUI, self).__init__()
        self.parent = parent
        self.resize(800, 300)
        self.setWindowIcon(self.style().standardIcon(getattr(QtWidgets.QStyle,"SP_TitleBarMenuButton")))
        self.setWindowTitle("Toolkit Manager")
        
        # Array of names and dict of paths/docs URL
        self.toolkitNames = []
        self.toolkitPaths = {}
        self.toolkitDocs = {}

        self.buildUI()
        self.setLayout(self.layout)
        
    # Build the UI. Possibly replace with a .ui file to simplify modification
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
        #self.buttonLayout.addWidget(self.btOpen)
        self.buttonLayout.addItem(vspace)
        
        self.layout.addItem(self.buttonLayout)
        
    # Show prompt to load toolkit and add to table
    def loadToolkit(self):
    
        # Need to get the folder that contains the toolkit config file
        path = os.path.abspath(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        if (path is not ''):
            if os.path.exists(os.path.join(path,"config.json")):
                data = utils._loadData(os.path.join(path, "config.json"))     
                
                # Data Validation
                if "name" not in data.keys():
                    QtWidgets.QMessageBox.warning(self, "Warning", "Toolkit config file does not contain 'name' parameter")
                    return
                elif data["name"] == "":
                    QtWidgets.QMessageBox.warning(self, "Warning", "Toolkit name cannot be an empty string")
                    return
                    
                if "docs" not in data.keys():
                    QtWidgets.QMessageBox.warning(self, "Warning", "Toolkit config file does not contain 'docs' parameter")
                    return
                    
                if "node_types" not in data.keys():
                    QtWidgets.QMessageBox.warning(self, "Warning", "Toolkit config file contains no nodes")
                    return
                if len(data["node_types"]) == 0:
                    QtWidgets.QMessageBox.warning(self, "Warning", "Toolkit config file contains no nodes")
                    return
                    
                name = data["name"]
                
                # Check if theres a matching name or path in the table
                for row in range(self.toolkitTable.rowCount()):
                    if self.toolkitTable.item(row, 0).text() == name:
                        QtWidgets.QMessageBox.warning(self, "Warning", "Toolkit with matching name already exists")
                        return
                    
                    if self.toolkitTable.item(row, 2).text() == path:
                        QtWidgets.QMessageBox.warning(self, "Warning", "Toolkit with matching path already exists")
                        return 
            
                self.addRow(name, path)
                self.toolkitDocs[name] = data["docs"]
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
        tksFile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "toolkits", "toolkitConfig.json")
        tks = utils._loadData(tksFile)
        for tk in tks:
            self.addRow(tks[tk]["name"], tks[tk]["path"], tks[tk]["show"])
            self.toolkitDocs[tks[tk]["name"]] = tks[tk]["docs"]
        self.reloadToolkits()
            
        
    # Generates the initial json file based on the toolkits available in the WARIO root folder
    def genSettings(self):
        base = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "toolkits"))
        for root, directories, files in os.walk(base):
            for dir in directories:
                if dir != "__pycache__":
                    configData = utils._loadData(os.path.join(base, dir, "config.json"))
                    self.addRow(configData["name"], os.path.join(base, dir))
                    self.toolkitDocs[configData["name"]] = configData["docs"]
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
        
    # Updates the WARIO UI to make sure that the correct toolkits are showing and save the list
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
            docs = os.path.normpath(os.path.join(path, self.toolkitDocs[name]))
            data[name] = {"name" : name, "show" : show, "path" : path, "docs" : docs}
        
        # Update the base UI
        self.parent.parent.buildToolkitToggles()
        self.parent.helpUI.buildToolkitHelp()
        
        # Save the config file
        filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "toolkits", "toolkitConfig.json")
        utils._saveData(filePath=filepath, data=data)
        
    