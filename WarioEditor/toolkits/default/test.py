from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets, QtCore, QtGui
from extensions.customWidgets import *
import importlib
import inspect

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
        
    def getProperties(self):
        return
        
      
class GlobalTextbox(GlobalWindowWidget):
    def __init__(self):
        super(GlobalTextbox, self).__init__()
        
        self.cls = "GlobalTextbox"
        self.file = "extensions.globalWidgets"
        
        self.textbox = QtWidgets.QLineEdit()
        self.textbox.setFrame(False)
        
        self.layout.addWidget(self.textbox)
        
    def getData(self):
        return self.textbox.text()
        
    def setData(self, gb):
        self.textbox.setText(gb["value"])