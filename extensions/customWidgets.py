from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import uic

# Mimics a cell checkbox but is centred
class CentredCellCheckbox(QtWidgets.QWidget):
    def __init__(self):
        super(CentredCellCheckbox, self).__init__()
        self.checkbox = QtWidgets.QCheckBox("")
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.checkbox)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)
        
    def setChecked(self, state):
        self.checkbox.setChecked(state)
        
    def isChecked(self):
        return self.checkbox.isChecked()
        
    def connect(self, func):
        self.checkbox.toggled.connect(func)

class GlobalSaveTabs(QtWidgets.QTabWidget):
    def __init__(self, saveTypes, saveDialogString, settings, name = ""):
        super(GlobalSaveTabs, self).__init__()
        self.globalName = ""
        self.globalFolder = ""
        self.name = name
        
        self.globalTab = QtWidgets.QWidget()
        self.globalLayout = QtWidgets.QFormLayout()
        self.customTab = QtWidgets.QWidget()
        self.customLayout = QtWidgets.QFormLayout()
        
        self.previewLabel = QtWidgets.QLabel("")
        
        self.globalFilename = QtWidgets.QLineEdit()  
        if "globalFilename" + name in settings.keys():
            self.globalFilename.setText(settings["globalFilename" + name])
        label = QtWidgets.QLabel("File Identifier")
        self.globalLayout.addRow(label, self.globalFilename)
        
        self.globalFileType = QtWidgets.QComboBox()
        self.globalFileType.addItems(saveTypes)
        if "globalFileType" + name in settings.keys():
            self.globalFileType.setCurrentText(settings["globalFileType" + name])
        label = QtWidgets.QLabel("File type")
        self.globalLayout.addRow(label, self.globalFileType)
        
        self.globalFilename.textChanged.connect(self.updatePreview)
        self.globalFileType.currentTextChanged.connect(self.updatePreview)
        
        label = QtWidgets.QLabel("Filename:")
        self.globalLayout.addRow(label, self.previewLabel)
        
        self.globalTab.setLayout(self.globalLayout)
        self.addTab(self.globalTab, "Use Global Filename")
         
        label = QtWidgets.QLabel("File Location")
        self.saveLoc = saveWidget(self, saveDialogString)
        if "saveLoc" + name in settings.keys():
            self.saveLoc.textbox.setText(settings["saveLoc" + name])
        self.customLayout.insertRow(-1, label, self.saveLoc)
        
        self.customTab.setLayout(self.customLayout)
        self.addTab(self.customTab, "Use Custom Filename")
        
        if "currentTab" + name in settings.keys():
            self.setCurrentIndex(settings["currentTab" + name])
    
    def updateGlobals(self, globals):
        if "Output Filename" not in globals.keys():
            return
        if "Output Folder" not in globals.keys():
            return
        self.globalName = globals["Output Filename"]["value"]
        self.globalFolder = globals["Output Folder"]["value"]
        
        self.updatePreview("")
        
    def updatePreview(self, signal):
        self.previewLabel.setText(self.globalName + "_" + self.globalFilename.text() + "." + self.globalFileType.currentText().lower())

    def genSettings(self, settings):
        settings["saveLoc" + self.name] = self.saveLoc.textbox.text()
        settings["globalFilename" + self.name] = self.globalFilename.text()
        settings["globalFileType" + self.name] = self.globalFileType.currentText()
        settings["currentTab" + self.name] = self.currentIndex()
        
    def genVars(self, vars):
        if self.currentIndex() == 0:
            vars["saveGraph" + self.name] = self.globalFolder + self.globalName + "_" + self.globalFilename.text() + "." + self.globalFileType.currentText().lower()
            vars["globalSaveStart" + self.name] = self.globalFolder + "\\"
            vars["globalSaveEnd" + self.name] = "_" + self.globalFilename.text() + "." + self.globalFileType.currentText().lower()
        else:
            vars["saveGraph" + self.name] = self.saveLoc.textbox.text()

class BatchSavePanel(GlobalSaveTabs):
    def __init__(self, saveTypes, saveDialogString, settings, name = ""):
        super(BatchSavePanel, self).__init__(saveTypes, saveDialogString, settings, name)
        
    def updatePreview(self, signal):
        self.previewLabel.setText(self.globalFilename.text() + "." + self.globalFileType.currentText().lower())

    def genVars(self, vars):
        if self.currentIndex() == 0:
            vars["saveGraph" + self.name] = self.globalFolder + "\\" + self.globalFilename.text() + "." + self.globalFileType.currentText().lower()
        else:
            vars["saveGraph" + self.name] = self.saveLoc.textbox.text()

class BatchSaveTab(QtWidgets.QWidget):
    def __init__(self, name, type, settings, pkl = True):
    
        super(BatchSaveTab, self).__init__()
        
        self.name = name
        self.type = type
        
        self.layout = QtWidgets.QVBoxLayout()

        if type == "data":
            saveTypes = ["NPZ"] 
            saveDialogString = "Numpy File (*.npz)"
            self.tabBox = BatchSavePanel(saveTypes, saveDialogString, settings, name)
            
            self.saveData = LinkedCheckbox("Save Data", self.tabBox)
            if "toggleSave" + name in settings.keys():
                self.saveData.setChecked(settings["toggleSave" + name])
            else:
                self.saveData.setChecked(True)
            self.layout.addWidget(self.saveData)
            
        elif type == "graph":
            if pkl == True:
                saveTypes = ["PNG", "PDF", "PKL"]
                saveDialogString = "PNG image (*.png);; PDF (*.pdf);; Pickle (*.pkl)"
            else:
                saveTypes = ["PNG", "PDF"]
                saveDialogString = "PNG image (*.png);; PDF (*.pdf)"
            self.tabBox = BatchSavePanel(saveTypes, saveDialogString, settings, name)
            
            graphLayout = QtWidgets.QHBoxLayout()
            
            self.showGraph = QtWidgets.QCheckBox("Show Graph")
            if "toggleShow" + name in settings.keys():
                self.showGraph.setChecked(settings["toggleShow" + name ])
            else:
                self.showGraph.setChecked(True)
            
            self.saveData = LinkedCheckbox("Save Graph", self.tabBox)
            if "toggleSave" + name in settings.keys():
                self.saveData.setChecked(settings["toggleSave" + name ])
            else:
                self.saveData.setChecked(True)
            
            
            graphLayout.addWidget(self.showGraph)
            graphLayout.addWidget(self.saveData)

            self.layout.addItem(graphLayout)
        
        self.layout.addWidget(self.tabBox)
        
        self.setLayout(self.layout)
        
    def genSettings(self, settings, vars):
        
        settings["toggleSave" + self.name ] = self.saveData.isChecked()
        vars["toggleSave" + self.name] = self.saveData.isChecked()
        if self.type == "graph":
            settings["toggleShow" + self.name] = self.showGraph.isChecked()
            vars["toggleShow" + self.name] = self.showGraph.isChecked()
            
        self.tabBox.genSettings(settings)
        self.tabBox.genVars(vars)
        
    def updateGlobals(self, globals):
        self.tabBox.updateGlobals(globals)
                
class ExpandingTable(QtWidgets.QTableWidget):
    def __init__(self, name, settings):
        super(ExpandingTable, self).__init__(1, 1)
        
        self.cellChanged.connect(self.checkRowCount)
        
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.setHorizontalHeaderLabels(["data"])
        
        if name + "Values" in settings.keys():
            for i in range(len(settings[name + "Values"])):
                self.insertRow(self.rowCount())
                self.setItem(i, 0, QtWidgets.QTableWidgetItem(settings[name + "Values"][str(i)]))

        
    def checkRowCount(self, i, j):
        if self.item(self.rowCount() - 1, 0) != None:
            if self.item(self.rowCount() - 1, 0).text() != "":
                self.insertRow(self.rowCount())
        if self.item(self.rowCount() - 2, 0) != None:    
            if self.item(self.rowCount() - 2, 0).text() == "":
                self.removeRow(self.rowCount() - 1)
            
            
    def getSettings(self, name, var, settings):
    
        varDict = {}
        settingsDict = {}
        
        for i in range(self.rowCount() - 1):
            settingsDict[i] = self.item(i, 0).text()
            varDict[self.item(i, 0).text()] = i + 1
            
        var[name] = varDict
        settings[name + "Values"] = settingsDict
        
# Spinbox linked to another spinbox so they cant be higher/lower
class LinkedSpinbox(QtWidgets.QSpinBox):
    def __init__(self):
        super(LinkedSpinbox, self).__init__()
        self.linkedWidget = None
        self.linkType = None
        self.valueChanged.connect(self.updateLink)
        
    def linkWidgets(self, widget, type):
        self.linkedWidget = widget
        self.linkedType = type
        self.updateLink(self.value())
    
    def updateLink(self, value):
        if self.linkedWidget == None:
            return
            
        # Linked widget is always lower
        if self.linkedType == "Lower":
            self.linkedWidget.setMaximum(value - 1)
            
        # Linked widget is always higher
        elif self.linkedType == "Higher":
            self.linkedWidget.setMinimum(value + 1)
    
    
# Same as above but for doubles
class LinkedDoubleSpinbox(QtWidgets.QDoubleSpinBox):
    def __init__(self):
        super(LinkedDoubleSpinbox, self).__init__()
        self.linkedWidget = None
        self.linkType = None
        self.valueChanged.connect(self.updateLink)
        
    def linkWidgets(self, widget, type):
        self.linkedWidget = widget
        self.linkedType = type
        self.updateLink(self.value())
    
    def updateLink(self, value):
        if self.linkedWidget == None:
            return
            
        # Linked widget is always lower
        if self.linkedType == "Lower":
            self.linkedWidget.setMaximum(value - 0.01)
            
        # Linked widget is always higher
        elif self.linkedType == "Higher":
            self.linkedWidget.setMinimum(value + 0.01)

# Checkbox that is linked to another widget and enables/disables it
class LinkedCheckbox(QtWidgets.QCheckBox):
    def __init__(self, text, widget):
        super(LinkedCheckbox, self).__init__(text)
        self.linkedWidget = widget
        self.stateChanged.connect(self.updateLink)
        self.setChecked(False)
        self.updateLink(0)
        
    def updateLink(self, state):
        if state == 0:
            self.linkedWidget.setEnabled(False)
        else:
            self.linkedWidget.setEnabled(True)
            
    def buildLinkedCheckbox(self, name, settings):
        if name + "Checked" in settings.keys():
            self.setChecked(settings[name + "Checked"])
            
            if isinstance(self.linkedWidget, QtWidgets.QSpinBox):
                self.linkedWidget.setMaximum(settings[name + "Max"])
                self.linkedWidget.setMinimum(settings[name + "Min"])
                self.linkedWidget.setValue(settings[name + "Value"])
                
            if isinstance(self.linkedWidget, QtWidgets.QComboBox):
                self.linkedWidget.setCurrentIndex(settings[name + "Index"])
        
    def getSettings(self, name, varList, settingList):

        settingList[name + "Checked"] = self.isChecked()
        
        # Spinbox results
        if isinstance(self.linkedWidget, QtWidgets.QSpinBox):
            if self.isChecked():
                varList[name] = self.linkedWidget.value()
            else:
                varList[name] = None

            settingList[name + "Max"] = self.linkedWidget.maximum()
            settingList[name + "Min"] = self.linkedWidget.minimum()
            settingList[name + "Value"] = self.linkedWidget.value()
            
        if isinstance(self.linkedWidget, QtWidgets.QComboBox):
            if self.isChecked():
                varList[name] = self.linkedWidget.currentIndex()
            else:
                varList[name] = None
                
            settingList[name + "Index"] = self.linkedWidget.currentIndex() 
            
# QTableWidget that forces the first column to be unique
# Attempts to use the same value twice reverts it to its previous value
class UniqueNameTable(QtWidgets.QTableWidget):
    def __init__(self, error):
        super(UniqueNameTable, self).__init__()
        self.cellChanged.connect(self.checkUniqueNames)
        self.prevNames = {}
        self.varNameCounter = 0
        self.error = error
        
    def checkUniqueNames(self, row, column):
        # if the name row
        if column == 0: 
            item = self.item(row, column)
            # if row already exists
            if row in self.prevNames:
                # if no change to text then exit
                if self.prevNames[row] == item.text():
                    return
                # If the name is already in use or is empty
                if item.text() in self.prevNames.values() or item.text() == "":
                    item.setText(self.prevNames[row])
                    QtWidgets.QMessageBox.critical(self, "ERROR", self.error)
                    
                # Hook for function that runs when name changs
                self.changedTextHook(self.prevNames[row])
  
            self.prevNames[row] = item.text()
            
    def updateNames(self):
        self.prevNames = {}
        for row in range(0, self.rowCount()):
            self.prevNames[row] = self.item(row, 0).text()  
            
    def changedTextHook(self, row):
        return
        
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
                                             dataType = self.globalsList[self.currentText()]["attrType"])
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
    def __init__(self, parent, types = "All files (*.*)"):
        super(loadWidget, self).__init__()
        self.parent = parent
        self.setSpacing(5)
        
        self.textbox = QtWidgets.QLineEdit()
        self.button = QtWidgets.QPushButton("Browse")
        self.button.clicked.connect(self.loadFile)
        self.addWidget(self.textbox)
        self.addWidget(self.button)
        
    def loadFile(self):
        f = QtWidgets.QFileDialog.getOpenFileName()[0]
        if f is not "":
            self.textbox.setText(f)
        
    def loadSettings(self, settings):
        if "filename" in settings.keys():
            self.textbox.setText(settings["filename"])
    
    def genSettings(self, settings, vars):
        settings["filename"] = self.textbox.text()
        vars["filename"] = self.textbox.text()
        
        
class saveWidget(loadWidget):
    def __init__(self, parent, types = "All files (*.*)"):
        super(saveWidget, self).__init__(parent)
        self.button.clicked.disconnect()
        self.button.clicked.connect(self.saveFile)
        self.types = types
        
    def saveFile(self):
        f = QtWidgets.QFileDialog.getSaveFileName(filter = self.types)[0]
        if f is not "":
            self.textbox.setText(f)
            
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