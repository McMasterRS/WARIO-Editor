from pipeline.Node import Node
from nodz.customSettings import CustomSettings
import mne
import numpy as np
import matplotlib.pyplot as plt

from PyQt5 import QtWidgets
from PyQt5 import QtCore

class EvokedPeakSettings(CustomSettings):
    def __init__(self, parent, settings):
        super(EvokedPeakSettings, self).__init__(parent, settings)
        
    # Build the settings UI
    def buildUI(self, settings):
        self.layout = QtWidgets.QFormLayout() 
        self.setLayout(self.layout)
        
    def genSettings(self):
    
        settings = {}
        vars = {}
        
        settings["settingsFile"] = self.settings["settingsFile"]
        settings["settingsClass"] = self.settings["settingsClass"]
        
        self.parent.settings = settings
        self.parent.variables = vars

class evokedPeak(Node):

    def __init__(self, name, params):
        super(evokedPeak, self).__init__(name, params)
    
    def process(self):
    
        evokedData = self.args["Evoked Data"]
        for evoked in evokedData:
            chName, latency, amplitude = evoked.get_peak(return_amplitude = True)
            fig = evoked.plot_joint(title = "Peak for event ID {0}".format(evoked.comment),
                              times=latency, show = False)    
            fig.show()
            
        
        return