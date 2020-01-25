from PyQt5 import QtWidgets
from .CustomWidgets import *
import importlib
import inspect

# Combobox that lists the types of global variables
class TypeComboBox(QtWidgets.QComboBox):
    def __init__(self):
        super(TypeComboBox, self).__init__()
        # Custom option must remain last for setEditState to work properly
        self.types = ["String", "Int", "Float", "Bool", "File", "Folder", "List", "Custom"]
        self.addItems(self.types)
        self.setCurrentIndex(0)
        self.setEditable(False)
        #self.currentIndexChanged.connect(self.setEditState)
        
    # Enables editing if custom box selected
    def setEditState(self, index):
        if index == len(self.types) - 1:
            self.setEditable(True)
        else:
            self.setEditable(False)

# Base class that all global widgets will import
class GlobalWindowWidget(QtWidgets.QWidget):
    def __init__(self):
        super(GlobalWindowWidget, self).__init__()
        
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setContentsMargins(1, 1, 1, 1)
        self.layout.setSpacing(2)
        self.setLayout(self.layout)
        
        self.toolkit = "wario"
        
        self.cls = []
        self.file = "wario.GlobalWidgets"
        
    def getData(self):
        return None
        
    def setData(self):
        return
        
    def getProperties(self):
        return
        
      
class GlobalTextbox(GlobalWindowWidget):
    def __init__(self):
        super(GlobalTextbox, self).__init__()
        
        self.cls = "GlobalTextbox"
        
        self.textbox = QtWidgets.QLineEdit()
        self.textbox.setFrame(False)
        
        self.layout.addWidget(self.textbox)
        
    def getData(self):
        return self.textbox.text()
        
    def setData(self, gb):
        self.textbox.setText(gb["value"]) 
        
class GlobalSpinbox(GlobalWindowWidget):
    def __init__(self):
        super(GlobalSpinbox, self).__init__()
        
        self.cls = "GlobalSpinbox"
        
        self.spinbox = QtWidgets.QSpinBox()
        self.layout.addWidget(self.spinbox)
        
    def getData(self):
        return self.spinbox.value()
        
    def setData(self, gb):
        self.spinbox.setValue(gb["value"])
               
class GlobalDoubleSpinbox(GlobalWindowWidget):
    def __init__(self):
        super(GlobalDoubleSpinbox, self).__init__()
        
        self.cls = "GlobalDoubleSpinbox"
        
        self.spinbox = QtWidgets.QDoubleSpinBox()
        self.layout.addWidget(self.spinbox)
        
    def getData(self):
        return self.spinbox.value()
        
    def setData(self, gb):
        self.spinbox.setValue(gb["value"])
        
class GlobalCheckbox(GlobalWindowWidget):
    def __init__(self):
        super(GlobalCheckbox, self).__init__()
        
        self.cls = "GlobalCheckbox"
        
        self.checkbox = QtWidgets.QCheckBox()
        self.layout.addWidget(self.checkbox)
        
    def getData(self):
        return self.checkbox.isChecked()
        
    def setData(self, gb):
        self.checkbox.setChecked(gb["value"])

class GlobalFileSelect(GlobalWindowWidget):
    def __init__(self):
        super(GlobalFileSelect, self).__init__()
        
        self.cls = "GlobalFileSelect"
        
        self.fileBox = QtWidgets.QLineEdit()
        
        self.saveButton = QtWidgets.QPushButton("Load")
        width = self.saveButton.fontMetrics().boundingRect("Load").width() + 15
        self.saveButton.setMaximumWidth(width)
        self.saveButton.clicked.connect(self.getFile)
        
        self.layout.addWidget(self.fileBox)
        self.layout.addWidget(self.saveButton)
        
    def getFile(self):
        dialog = QtWidgets.QFileDialog.getOpenFileName(self, "Select File")
        if (dialog[0] != ''):
            self.fileBox.setText(dialog[0])
        
    def getData(self):
        return(self.fileBox.text())
        
    def setData(self, gb):
        self.fileBox.setText(gb["value"])
        
class GlobalFolderSelect(GlobalFileSelect):
    def __init__(self):
        super(GlobalFolderSelect, self).__init__()
        self.cls = "GlobalFolderSelect"
        
    def getFile(self):
        dialog = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")
        if (dialog != ''):
            self.fileBox.setText(dialog)
        
class GlobalListInput(GlobalWindowWidget):
    def __init__(self):
        super(GlobalListInput, self).__init__()
        
        self.cls = "GlobalListInput"
        
        self.openButton = QtWidgets.QPushButton("Edit")
        self.openButton.clicked.connect(self.openMenu)
        self.layout.addWidget(self.openButton)
        
        self.menuWindow = GlobalListWindow()
        
    def getData(self):
        return self.menuWindow.getData()
        
    def setData(self, gb):
        self.menuWindow.setData(gb)
        
    def openMenu(self):
        self.menuWindow.show()
        
class GlobalListWindow(QtWidgets.QWidget):
    def __init__(self):
        super(GlobalListWindow, self).__init__()
        
        self.layout = QtWidgets.QVBoxLayout()
        self.table = ExpandingTable("", {})
        self.layout.addWidget(self.table)
        
        self.setLayout(self.layout)
        
    def getData(self):
        data = []

        for i in range(self.table.rowCount() - 1):
            data.append(self.table.item(i, 0).text())
        
        return data
        
    def setData(self, gb):
        vals = gb["value"]
        for i in range(len(vals)):
            self.table.insertRow(self.table.rowCount())
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(vals[i]))
            
class GlobalTwoColumnListInput(GlobalListInput):
    def __init__(self):
        super(GlobalTwoColumnListInput, self).__init__()
        
        self.cls = "GlobalTwoColumnListInput"
        self.menuWindow = GlobalTableWindow(2)      

    def setData(self, gb):
        self.menuWindow.setData(gb)
        self.menuWindow.table.setHorizontalHeaderLabels(gb["properties"]["headers"])
        
    def getProperties(self):
        headers = []
        for i in range(self.menuWindow.table.columnCount()):
            if self.menuWindow.table.horizontalHeaderItem(i) != None:
                headers.append(self.menuWindow.table.horizontalHeaderItem(i).text())
        return {"headers" : headers}
            
class GlobalTableWindow(QtWidgets.QWidget):
    def __init__(self, columns):
        super(GlobalTableWindow, self).__init__()
        
        self.layout = QtWidgets.QVBoxLayout()
        self.table = ExpandingTable("", {})
        self.table.setColumnCount(columns)
        self.layout.addWidget(self.table)
        
        self.setLayout(self.layout)
        
    def getData(self):
        data = []
        
        for i in range(self.table.rowCount() - 1):
            rowData = []
            
            for j in range(self.table.columnCount()):
                rowData.append(self.table.item(i, j).text())
                
            data.append(rowData)
        
        return data
        
    def setData(self, gb):
        vals = gb["value"]
        self.table.blockSignals(True)
        for i, row in enumerate(vals):
            self.table.insertRow(self.table.rowCount())
            for j, val in enumerate(row):
                self.table.setItem(i, j, QtWidgets.QTableWidgetItem(val))
        self.table.blockSignals(False)
            
        
class GlobalCustomWidget(GlobalWindowWidget):
    def __init__(self):
        super(GlobalCustomWidget, self).__init__()
        
        self.cls = "GlobalCustomWidget"
        
        # "Load" if file hasnt been selected, "Open" if it has
        self.state = "Load"
        
        self.window = []
        
        # Widgets for load view
        self.loadWidget = QtWidgets.QWidget()
        self.loadLayout = QtWidgets.QHBoxLayout()
        self.loadLayout.setContentsMargins(0, 0, 0, 0)
        self.loadLayout.setSpacing(2)
        self.fileBox = QtWidgets.QLineEdit()
        self.saveButton = QtWidgets.QPushButton("Load")
        width = self.saveButton.fontMetrics().boundingRect("Load").width() + 15
        self.saveButton.setMaximumWidth(width)
        self.saveButton.clicked.connect(self.getFile)
        
        self.loadLayout.addWidget(self.fileBox)
        self.loadLayout.addWidget(self.saveButton)
        self.loadWidget.setLayout(self.loadLayout)
        
        # Widgets for custom input view
        self.showWidget = QtWidgets.QWidget()
        self.showLayout = QtWidgets.QHBoxLayout()
        self.showLayout.setContentsMargins(0, 0, 0, 0)
        self.showButton = QtWidgets.QPushButton("Show")
        self.showButton.clicked.connect(self.showWindow)
        
        self.showLayout.addWidget(self.showButton)
        self.showWidget.setLayout(self.showLayout)
        
        self.layout.addWidget(self.loadWidget)
        self.setLayout(self.layout)
        
    def getData(self):
        if self.state == "Load":
            return self.fileBox.text()
        else:
            return self.window.getData()
            
    def setData(self, gb):
        self.fileBox.setText(gb["value"])
        if gb["properties"]["state"] == "Open":
            self.state = "Open"
            self.swapState(gb["properties"]["class"])
            self.window.setData(gb)
            
    def getProperties(self):
        if self.state == "Load":
            return {"state" : "Load"}
        else:
            return self.window.getProperties()
            
    def getFile(self):
        f = QtWidgets.QFileDialog.getOpenFileName(filter = "Python Files (*.py)")[0]
        if f is not "":
            self.fileBox.setText(f)
            self.swapState()
            
    def showWindow(self):
        self.window.show()
    
    def swapState(self, cls = None):
        # Load the relevant module
        spec = importlib.util.spec_from_file_location(name = "Custom", location = self.fileBox.text())
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if cls is None:
            # List the classes in the module for the user to choose
            classList = [m[0] for m in inspect.getmembers(module, inspect.isclass) if m[1].__module__ == 'Custom']
            
            cls, ok = QtWidgets.QInputDialog.getItem(self, "Select Class", "Class:", classList, 0, False)
            if ok is False:
                return
        
        self.window = getattr(module, cls)()
        self.window.show()
        self.state = "Open"
        self.layout.removeWidget(self.loadWidget)
        self.layout.addWidget(self.showWidget)
        