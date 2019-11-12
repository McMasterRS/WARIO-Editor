from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets, QtCore, QtGui

# Combobox that lists the types of global variables
class TypeComboBox(QtWidgets.QComboBox):
    def __init__(self):
        super(TypeComboBox, self).__init__()
        # Custom option must remain last for setEditState to work properly
        self.types = ["String", "Int", "Float", "Bool", "File", "Folder", "Custom"]
        self.addItems(self.types)
        self.setCurrentIndex(0)
        self.setEditable(False)
        self.currentIndexChanged.connect(self.setEditState)
        
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
        
        self.cls = []
        self.file = []
        
    def getData(self):
        return None
        
    def setData(self):
        return
        
    def saveProperties(self, gb):
        return
        
        
class GlobalTextbox(GlobalWindowWidget):
    def __init__(self):
        super(GlobalTextbox, self).__init__()
        
        self.cls = "GlobalTextbox"
        self.file = "nodz.globalWidgets"
        
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
        self.file = "nodz.globalWidgets"
        
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
        self.file = "nodz.globalWidgets"
        
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
        self.file = "nodz.globalWidgets"
        
        self.checkbox = QtWidgets.QCheckbox()
        self.layout.addWidget(self.checkbox)
        
    def getData(self):
        return self.checkbox.isChecked()
        
    def setData(self):
        self.setChecked(gb["value"])

class GlobalFileSelect(GlobalWindowWidget):
    def __init__(self):
        super(GlobalFileSelect, self).__init__()
        
        self.cls = "GlobalFileSelect"
        self.file = "nodz.globalWidgets"
        
        self.fileBox = QtWidgets.QLineEdit()
        self.fileBox.setFrame(False)
        
        self.saveButton = QtWidgets.QPushButton("Load")
        width = self.saveButton.fontMetrics().boundingRect("Load").width() + 15
        self.saveButton.setMaximumWidth(width)
        self.saveButton.clicked.connect(self.getFile)
        
        self.layout.addWidget(self.fileBox)
        self.layout.addWidget(self.saveButton)
        
    def getFile(self):
        self.fileBox.setText("")
        
    def getData(self):
        return(self.fileBox.text())
        
    def setData(self, gb):
        self.fileBox.setText(gb["value"])
        
class GlobalFolderSelect(GlobalFileSelect):
    def __init__(self):
        super(GlobalFolderSelect, self).__init__()
        self.cls = "GlobalFolderSelect"
        
    def getFile(self):
        self.fileBox.setText("")
        
class GlobalListInput(GlobalWindowWidget):
    def __init__(self):
        super(GlobalListInput, self).__init__()
        
        self.cls = "GlobalListInput"
        self.file = "nodz.globalWidgets"
        
        
        