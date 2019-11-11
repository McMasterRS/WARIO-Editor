from pipeline.Node import Node
from nodz.customSettings import CustomSettings
import mne
import numpy as np
import matplotlib.pyplot as plt

from PyQt5 import QtWidgets
from PyQt5 import QtCore

class evokedPeak(Node):

    def __init__(self, name, params):
        super(evokedPeak, self).__init__(name, params)
    
    def process(self):
    
        evokedData = self.args["Evoked Data"]
        for i, evoked in enumerate(evokedData):
            chName, latency, amplitude = evoked.get_peak(return_amplitude = True)
            fig = evoked.plot_joint(title = "Peak for event ID {0}".format(evoked.comment), times=latency, show = False)    
            
            if self.parameters["toggleSaveGraph"] is not None:
                f = self.parameters["saveGraphGraph"]
                type = f.split(".")[-1]
                name = f.split(".")[0]
                f = name + "_{0}.".format(i) + type
                if type == "png":
                    fig.savefig(f, format = "png")
                elif type == "pdf":
                    fig.savefig(f, format = "pdf")
                elif type == "pkl":
                    pickle.dump(fig, open(f, "wb"))
            
            if self.parameters["toggleShowGraph"] == True:
                fig.show()
            else:
                plt.close(fig)
            
        
        return