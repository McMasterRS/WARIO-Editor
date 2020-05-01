from PyQt5 import QtWidgets, QtCore, uic
import os, json

class WarioSettings(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        
        self.installEventFilter(self)

        # Loads UI file and defines file location for saved settings
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)),"WarioSettings.ui"), self)
        self.file = os.path.join(os.path.dirname(os.path.realpath(__file__)),"..", "editorConfig.json")
        
        # Connect function calls to UI elements
        self.rbCustom.toggled.connect(self.toggleActive)
        self.btLoadDisplay.clicked.connect(self.loadDisplay)
        self.toggleActive(False)
        
        # Load settings if file exists, otherwise generate new file
        if os.path.exists(self.file):
            self.loadSettings()
        else:
            self.genSettings()
            
    # Catches window close/loss of focus events
    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.Close:
            self.genSettings()
            event.accept()
        elif event.type() == QtCore.QEvent.WindowDeactivate:
            self.genSettings()
            event.accept()
            
        return False
        
    # Toggles the custom runtime controls on and off depending on 
    # the state of the custom radio button
    def toggleActive(self, enabled):
        if enabled:
            self.tbDisplay.setEnabled(True)
            self.btLoadDisplay.setEnabled(True)
        else:
            self.tbDisplay.setEnabled(False)
            self.btLoadDisplay.setEnabled(False)
            
    # Loads a custom runtime window
    def loadDisplay(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self, "Select Display File", filter = "Python Files (*.py)")[0]
        if path != "":
            self.tbDisplay.setText(path)
            
    # Loads state of the settings window from file
    def loadSettings(self):
        
        with open(self.file) as file:
            data = json.load(file)
        
            self.cbThreadless.setChecked(data["threadless"])
            self.cbSavePrompt.setChecked(data["savePrompt"])
            self.rbDefault.setChecked(data["rbDefault"])
            self.rbCustom.setChecked(data["rbCustom"])
            self.tbDisplay.setText(data["tbDisplay"])
            
            self.tbDisplay.setEnabled(data["rbCustom"])
            self.btLoadDisplay.setEnabled(data["rbCustom"])
            
        file.close()
        
    # Collects the current state of the settings window and dumps to file
    def genSettings(self):
        
        data = {}
        
        data["threadless"] = self.cbThreadless.isChecked()
        data["savePrompt"] = self.cbSavePrompt.isChecked()
        data["rbDefault"] = self.rbDefault.isChecked()
        data["rbCustom"] = self.rbCustom.isChecked()
        data["tbDisplay"] = self.tbDisplay.text()
        
        f = open(self.file, "w")
        f.write(json.dumps(data, indent = 4, ensure_ascii = False))