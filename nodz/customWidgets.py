from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import uic

class TypeComboBox(QtWidgets.QComboBox):
    def __init__(self):
        super(TypeComboBox, self).__init__()
        self.types = ["Int", "Float", "String", "File", "Custom"]
        self.addItems(self.types)
        self.setCurrentIndex(0)
        self.setEditable(False)
        self.currentIndexChanged.connect(self.setEditState)
        
    def setEditState(self, index):
        if index == len(self.types) - 1:
            self.setEditable(True)
        else:
            self.setEditable(False)
        
        
class GlobalNodeComboBox(QtWidgets.QComboBox):
    def __init__(self, parentNode, loaded):
        super(GlobalNodeComboBox, self).__init__()
        self.globalsList = []
        self.parentNode = parentNode
        self.currentIndexChanged.connect(self.updateParent)    
        self.manual = not loaded
        
    # Update attribute of parent
    def updateParent(self):
    
        if self.manual == False:
            self.manual = True
            return
    
        if self.parentNode.type == "Get Global":
            plug = True
        else:
            plug = False
        
        while len(self.parentNode.attrs) > 0:
            self.parentNode._deleteAttribute(0)
        if self.currentText() is not "":
            self.parentNode._createAttribute(name = self.currentText(),
                                             index = -1,
                                             plug = plug,
                                             socket = not plug,
                                             preset = "attr_preset_1",
                                             dataType = self.globalsList[self.currentText()])
        self.parentNode.update()
        
    def updateGlobals(self, globals):
        if globals == self.globalsList:
            return  
        
        #self.manual = False
        self.globalsList = globals
        selected = self.currentText()
        self.clear()
        self.addItems(self.globalsList)
        if self.findText(selected) == -1:
            self.manual = True
            self.setCurrentIndex(0)
        else:
            self.manual = False
            self.setCurrentIndex(self.findText(selected))
        self.manual = True

# Loadbox widget with file dialog
class loadWidget(QtWidgets.QHBoxLayout):
    def __init__(self, parent):
        super(loadWidget, self).__init__()
        self.parent = parent
        self.textbox = QtWidgets.QLineEdit()
        self.button = QtWidgets.QPushButton("Load")
        self.button.clicked.connect(self.loadFile)
        self.addWidget(self.textbox)
        self.addWidget(self.button)
        
    def loadFile(self):
        f = QtWidgets.QFileDialog.getOpenFileName()[0]
        if f is not "":
            self.textbox.setText(f)
        self.parent.genSettings()
        
# Loadbox exclusively for loading custom widget code
class customWidget(loadWidget):
    def __init__(self, parent):
        super(customWidget, self).__init__(parent)
        self.tempSettings = {}
        
    def loadFile(self):
        f = QtWidgets.QFileDialog.getOpenFileName(directory='.', filter="Python source files (*.py)")[0]
        if f is not "":
            self.textbox.setText(f)
            self.buildCustomUI()
        else:
            return

    # Turns file selected in textbox into a setting UI
    def buildCustomUI(self):
        f = self.textbox.text()
        
        try:
            # Load in setting JSON
            spec = importlib.util.spec_from_file_location("getSettings", f)
            obj = importlib.util.module_from_spec(spec)
   
            spec.loader.exec_module(obj)
            self.parent.resetUI(custom = True)
            self.parent.buildUI(json.loads(obj.getSettings()), custom = True)
        except:
            QtWidgets.QMessageBox.critical(self.parent, "ERROR", "Unable to import settings")
            return
        
        i = 2
        # Fill in the values for the custom genned settings
        # Used when duplicating or loading
        for p in self.tempSettings:
            setting = self.tempSettings[p]
            if setting["type"] == "custombox":
                continue
            w = self.parent.layout.itemAt(i, 1)
            if setting["type"] == "textbox":
                if "text" in setting["params"]: w.widget().setText(setting["params"]["text"])
            elif setting["type"] == "spinbox":
                if "value" in setting["params"]: w.widget().setValue(setting["params"]["value"]) 
            elif setting["type"] == "checkbox":
                if "checked" in setting["params"]: w.widget().setChecked(setting["params"]["checked"]) 
            elif setting["type"] == "loadbox":
                if "text" in setting["params"]: w.textbox.setText(setting["params"]["text"])
            i += 1
            
        self.tempSettings = {}
        
        try:
            # Load in the attribute json
            spec = importlib.util.spec_from_file_location("getAttribs", f)
            obj = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(obj)
            attribs = json.loads(obj.getAttribs())
            
            # Delete existing attributes and their connections
            while len(self.parent.parent.attrs) > 0:
                self.parent.parent._deleteAttribute(0)
        except:
            QtWidgets.QMessageBox.critical(self.parent, "ERROR", "Unable to import attributes: ")
            return    

        # Create attributes
        for attrib in attribs:
            index = attribs[attrib]['index']
            name = attrib
            plug = attribs[attrib]['plug']
            socket = attribs[attrib]['socket']
            preset = attribs[attrib]['preset']
            dataType = attribs[attrib]['type']
            self.parent.parent._createAttribute(name=name,
                                            index=index,
                                            preset=preset,
                                            plug=plug,
                                            socket=socket,
                                            dataType=dataType)
        
        # Initialize the settings for saving/duplicating
        self.parent.genSettings()