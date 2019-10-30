from pipeline.Node import Node
from nodz.customSettings import CustomSettings
import mne
import numpy as np
import matplotlib.pyplot as plt

from PyQt5 import QtWidgets
from PyQt5 import QtCore

class EvokedCustomTimesSettings(CustomSettings):
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

class evokedCustomTimes(Node):

    def __init__(self, name, params):
        super(evokedCustomTimes, self).__init__(name, params)
    
    def process(self):
    
        evokedData = self.args["Evoked Data"]
        for evoked in evokedData:
        
            max = evoked.times[-1]
            chName, latency, amplitude = evoked.get_peak(return_amplitude = True)
            fig = evoked.plot_joint(title = "Event ID {0}".format(evoked.comment),
                              times=np.arange(max / 10.0, max, max / 10.0), show = False)      
                
            if self.parameters["saveGraph"] is not None:
                if "globalSaveStart" in self.parameters.keys():
                    f = self.parameters["globalSaveStart"] + self.global_vars["Output Filename"] + self.parameters["globalSaveEnd"]
                else:
                    f = self.parameters["saveGraph"]
                type = f.split(".")[-1]
                if type == "png":
                    fig.savefig(f, format = "png")
                elif type == "pdf":
                    fig.savefig(f, format = "pdf")
                elif type == "pkl":
                    pickle.dump(fig, open(f, "wb"))
                    
            if self.parameters["showGraph"] == True:
                fig.show()
            else:
                plt.close(fig)
        
        return