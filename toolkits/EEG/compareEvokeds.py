from pipeline.Node import Node
from nodz.customSettings import CustomSettings
import mne

from PyQt5 import QtWidgets
from PyQt5 import QtCore

class EvokedSettings(CustomSettings):
    def __init__(self, parent, settings):
        super(EvokedSettings, self).__init__(parent, settings)
        
    # Build the settings UI
    def buildUI(self, settings):
        self.layout = QtWidgets.QFormLayout()
        self.layout.addWidget(QtWidgets.QLabel("Event IDs"))
        self.eventIDWidget = ExpandingTable("eventIDs", settings)
        self.layout.addWidget(self.eventIDWidget)
        
        self.setLayout(self.layout)
        
    def genSettings(self):
    
        settings = {}
        vars = {}
        
        settings["settingsFile"] = self.settings["settingsFile"]
        settings["settingsClass"] = self.settings["settingsClass"]
        
        self.eventIDWidget.getSettings("eventIDs", vars, settings)
        
        self.parent.settings = settings
        self.parent.variables = vars

class compareEvokeds(Node):

    def __init__(self, name, params):
        super(compareEvokeds, self).__init__(name, params)
    
    def process(self):
        evokedData = self.args["Evoked Data"]
        evokedDict = {}
        for evoked in evokedData:
            evokedDict[evoked.comment] = evoked
        fig = mne.viz.plot_compare_evokeds(evokedDict, show = False)
        fig.show()