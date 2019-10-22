from pipeline.Node import Node
from nodz.customSettings import CustomSettings
import mne

from PyQt5 import QtWidgets
from PyQt5 import QtCore

class SaveEpochSettings(CustomSettings):
        
    def __init__(self, parent, settings):
        super(SaveEpochSettings, self).__init__(parent, settings)
        
    def buildUI(self, settings):
        self.layout = QtWidgets.QFormLayout()
        self.saveLayout = QtWidgets.QHBoxLayout()
        
        self.textbox = QtWidgets.QLineEdit()
        if "saveText" in settings.keys():
            self.textbox.setText(settings["saveText"])
        self.button = QtWidgets.QPushButton("Save")
        self.button.clicked.connect(self.selectFolder)
        self.saveLayout.addWidget(self.textbox)
        self.saveLayout.addWidget(self.button)
        
        self.label = QtWidgets.QLabel("File Location")
        self.layout.insertRow(-1, self.label, self.saveLayout)
        self.setLayout(self.layout)
        
    def genSettings(self):
        varList = {}
        settingList = {}
        
        settingList["settingsFile"] = self.settings["settingsFile"]
        settingList["settingsClass"] = self.settings["settingsClass"]
        
        varList["file"] = self.textbox.text()
        settingList["saveText"] = self.textbox.text()
        
        self.parent.variables = varList
        self.parent.settings = settingList
        
    def selectFolder(self):
        f = QtWidgets.QFileDialog.getSaveFileName(directory='.', filter="FIF files (*.fif)")[0]
        if f is not "":
            self.textbox.setText(f)
        

class saveEpochs(Node):

    def __init__(self, name, params):
        super(saveEpochs, self).__init__(name, params)
        assert (self.parameters["file"] is not ""), "ERROR: No filename given in 'Save Epochs' node. Please update the node settings and re-run"
        
    def process(self):
    
        epochs = self.args["Epochs"]
        epochs.save(self.parameters["file"], overwrite = True)
