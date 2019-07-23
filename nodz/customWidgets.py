from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import uic

# QTableWidget that forces the first column to be unique
# Attempts to use the same value twice reverts it to its previous value
class UniqueNameTable(QtWidgets.QTableWidget):
    def __init__(self):
        super(UniqueNameTable, self).__init__()
        self.cellChanged.connect(self.checkUniqueNames)
        self.prevNames = {}
        self.varNameCounter = 0
        
    def checkUniqueNames(self, row, column):
        # if the name row
        if column == 0: 
            item = self.item(row, column)
            # if row already exists
            if row in self.prevNames:
                # If the name is already in use or is empty
                if item.text() in self.prevNames.values() or item.text() == "":
                    item.setText(self.prevNames[row])
                    QtWidgets.QMessageBox.critical(self, "ERROR", "Global variables must have unique names")
                            
            self.prevNames[row] = item.text()

# Combobox that lists the types of global variables
class TypeComboBox(QtWidgets.QComboBox):
    def __init__(self):
        super(TypeComboBox, self).__init__()
        # Custom option must remain last for setEditState to work properly
        self.types = ["Int", "Float", "String", "File", "Custom"]
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
        
        
class GlobalNodeComboBox(QtWidgets.QComboBox):
    def __init__(self, parentNode, loaded, text):
        super(GlobalNodeComboBox, self).__init__()
        self.loaded = loaded
        self.loadText = text
        self.globalsList = []
        self.parentNode = parentNode
        self.currentIndexChanged.connect(self.updateParent) 
        self.manual = True
        
    # Update attribute of parent
    def updateParent(self):
        # Only run if the selected variable is changed
        if self.manual == False or self.loaded == True:
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
                                             preset  = "attr_preset_1",
                                             dataType = self.globalsList[self.currentText()])
        self.parentNode.update()
        
    def updateGlobals(self, globals):
        # If no change was made exit
        if globals == self.globalsList:
            return  
        
        # Sets the selected text to the loaded value if the 
        # box was just loaded
        if self.loaded == True:
            selected = self.loadText
        else:
            selected = self.currentText()
        
        # Checks if the currently selected variable was changed
        #if selected in globals and selected in self.globalsList:
        #    if globals[selected] == self.globalsList[selected]:
        #        return
        
        self.globalsList = globals

        self.manual = False
        self.clear()
        self.addItems(self.globalsList)
        self.manual = True
        
        if self.findText(selected) == -1:
            self.setCurrentIndex(0)
            self.updateParent()
        else:
            self.setCurrentIndex(self.findText(selected))
            
        self.loaded = False
        

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