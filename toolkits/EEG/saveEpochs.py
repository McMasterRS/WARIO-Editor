from pipeline.Node import Node
from extensions.customSettings import CustomSettings
from extensions.customWidgets import GlobalSaveTabs
import mne

from PyQt5 import QtWidgets
from PyQt5 import QtCore

class SaveEpochSettings(CustomSettings):
        
    def __init__(self, parent, settings):
        super(SaveEpochSettings, self).__init__(parent, settings)
        
    def buildUI(self, settings):
        self.layout = QtWidgets.QVBoxLayout()
        self.tabs = GlobalSaveTabs(["FIF"], "FIF file (*.fif)", settings)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        
    def updateGlobals(self, globals):
        self.tabs.updateGlobals(globals)
        
    def genSettings(self):
        varList = {}
        settingList = {}
        
        settingList["settingsFile"] = self.settings["settingsFile"]
        settingList["settingsClass"] = self.settings["settingsClass"]
        
        self.tabs.genSettings(settingList)
        self.tabs.genVars(varList)
        
        varList["file"] = varList["saveGraph"]
        varList.pop("saveGraph")
        
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
        
        if "globalSaveStart" in self.parameters.keys():
            f = self.parameters["globalSaveStart"] + self.global_vars["Output Filename"] + self.parameters["globalSaveEnd"]
        else:
            f = self.parameters["file"]
        
        epochs.save(f, overwrite = True)
