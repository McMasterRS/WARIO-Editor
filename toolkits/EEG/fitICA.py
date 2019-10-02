from pipeline.Node import Node
from nodz.customSettings import CustomSettings
from nodz.customWidgets import LinkedCheckbox, LinkedSpinbox
import mne

from PyQt5 import QtWidgets
from PyQt5 import QtCore

class FitICASettings(CustomSettings):
    
    def __init__(self, parent, settings):
        super(FitICASettings, self).__init__(parent, settings)

    # Build the settings UI
    def buildUI(self, settings):
        self.layout = QtWidgets.QFormLayout()
        
        # ICA method
        label = QtWidgets.QLabel("ICA Method")
        self.methodWidget = QtWidgets.QComboBox()
        self.methodWidget.addItems(["fastica", "infomax", "extended-infomax", "picard"])
        if "method" in settings.keys():
            self.methodWidget.setCurrentText(settings["method"])
        self.layout.insertRow(-1, label, self.methodWidget)
        
        # Random state
        label = QtWidgets.QLabel("Fixed Random State")
        self.randomStateWidget = QtWidgets.QCheckBox()
        if "randomState" in settings.keys():
            self.randomStateWidget.setChecked(settings["randomState"])
        self.layout.insertRow(-1, label, self.randomStateWidget)
        
        # Start
        self.startWidget = LinkedSpinbox()
        self.startLabel = LinkedCheckbox("Start", self.startWidget)
        self.startLabel.buildLinkedCheckbox("start", self.settings)
        self.layout.insertRow(-1, self.startLabel, self.startWidget)
        
        # Stop
        self.stopWidget = LinkedSpinbox()
        self.stopLabel = LinkedCheckbox("Stop", self.stopWidget)
        self.stopLabel.buildLinkedCheckbox("stop", self.settings)
        self.layout.insertRow(-1, self.stopLabel, self.stopWidget)
        
        # Link start and stop
        self.startWidget.linkWidgets(self.stopWidget, "Higher")
        self.stopWidget.linkWidgets(self.startWidget, "Lower")
        
        # Skew
        self.skewWidget = QtWidgets.QSpinBox()
        self.skewLabel = LinkedCheckbox("Skew Criterion", self.skewWidget)
        self.skewLabel.buildLinkedCheckbox("skew", self.settings)
        self.layout.insertRow(-1, self.skewLabel, self.skewWidget)
        
        # Kurt
        self.kurtWidget = QtWidgets.QSpinBox()
        self.kurtLabel = LinkedCheckbox("Kurt Criterion", self.kurtWidget)
        self.kurtLabel.buildLinkedCheckbox("kurt", self.settings)
        self.layout.insertRow(-1, self.kurtLabel, self.kurtWidget)
        
        # Var
        self.varWidget = QtWidgets.QSpinBox()
        self.varLabel = LinkedCheckbox("Var Criterion", self.varWidget)
        self.varLabel.buildLinkedCheckbox("var", self.settings)
        self.layout.insertRow(-1, self.varLabel, self.varWidget)
        
        self.setLayout(self.layout)
        return
        
    def updateGlobals(self, globals):
        self.skewWidget.setMaximum(int(globals["Channel Count"]["value"]))
        self.kurtWidget.setMaximum(int(globals["Channel Count"]["value"]))
        self.varWidget.setMaximum(int(globals["Channel Count"]["value"]))
        self.stopWidget.setMaximum(int(globals["Data Length"]["value"]))
            
        
    # Return the values from each setting type
    def genSettings(self):
        
        varList = {}
        settingList = {}
        
        settingList["settingsFile"] = self.settings["settingsFile"]
        settingList["settingsClass"] = self.settings["settingsClass"]
        
        varList["method"] = self.methodWidget.currentText()
        settingList["method"] = varList["method"]
        
        varList["randomState"] = self.randomStateWidget.isChecked()
        settingList["randomState"] = varList["randomState"]
        
        self.startLabel.getSettings("start", varList, settingList)
        self.stopLabel.getSettings("stop", varList, settingList)
        self.skewLabel.getSettings("skew", varList, settingList)
        self.kurtLabel.getSettings("kurt", varList, settingList)
        self.varLabel.getSettings("var", varList, settingList)
    
        self.parent.variables = varList
        self.parent.settings = settingList


class fitICA(Node):

    def __init__(self, name, params):
        super(fitICA, self).__init__(name, params)
        
        if self.parameters["skew"] == "None":
            self.parameters["skew"] = None
            
        if self.parameters["kurt"] == "None":
            self.parameters["kurt"] = None
        
    def process(self):
    
        # Possibly will be epoch data - needs to work for both
        data = self.args["Raw"] 
        
        randomState = None
        if self.parameters["randomState"] == True:
            randomState = 1
            
        # Look at docs for this function https://mne.tools/dev/generated/mne.preprocessing.run_ica.html
        ica = mne.preprocessing.run_ica(data, 
                                    n_components=None, 
                                    max_pca_components=None,
                                    random_state=randomState, 
                                    start=self.parameters["start"],
                                    stop=self.parameters["stop"],
                                    ecg_ch=None, # Need to replace with autofill data taken from channel list
                                    skew_criterion=self.parameters["skew"], 
                                    kurt_criterion=self.parameters["kurt"], 
                                    var_criterion=self.parameters["var"],
                                    method=self.parameters["method"])

        return {"ICA Solution" : ica}