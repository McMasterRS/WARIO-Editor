from pipeline.Node import Node
from nodz.customSettings import CustomSettings
import mne
import matplotlib.pyplot as plt

from PyQt5 import QtWidgets
from PyQt5 import QtCore

class compareEvokeds(Node):

    def __init__(self, name, params):
        super(compareEvokeds, self).__init__(name, params)
    
    def process(self):
        evokedData = self.args["Evoked Data"]
        evokedDict = {}
        for evoked in evokedData:
            evokedDict[evoked.comment] = evoked
            
        fig = mne.viz.plot_compare_evokeds(evokedDict, show = False)

        if self.parameters["toggleSaveGraph"] is not None:
            f = self.parameters["saveGraphGraph"]
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