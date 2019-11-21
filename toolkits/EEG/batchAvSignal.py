from pipeline.Node import Node
from extensions.customSettings import CustomSettings

import mne
import numpy as np
import matplotlib.pyplot as plt

from extensions.customWidgets import LinkedSpinbox, BatchSavePanel, BatchSaveTab

from PyQt5 import QtWidgets
from PyQt5 import QtCore
                    
class BatchAvSignalSettings(CustomSettings):
    def __init__(self, parent, settings):
        super(BatchAvSignalSettings, self).__init__(parent, settings)
        
    def buildUI(self, settings):
        self.layout = QtWidgets.QVBoxLayout()
        
        self.tabs = QtWidgets.QTabWidget()
        
        self.dataSave = BatchSaveTab("Data", "data", settings)
        self.graphSave = BatchSaveTab("Graph", "graph", settings)
        
        self.tabs.addTab(self.dataSave, "Save Data")
        self.tabs.addTab(self.graphSave, "Save Graph")
        
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        
    def genSettings(self):
    
        settings = {}
        vars = {}
        
        settings["settingsFile"] = self.settings["settingsFile"]
        settings["settingsClass"] = self.settings["settingsClass"]
        
        self.dataSave.genSettings(settings, vars)
        self.graphSave.genSettings(settings, vars)
        
        self.parent.settings = settings
        self.parent.variables = vars
        
    def updateGlobals(self, globals):
        self.dataSave.updateGlobals(globals)
        self.graphSave.updateGlobals(globals)

class batchAvSignal(Node):
    def __init__(self, name, params):
        super(batchAvSignal, self).__init__(name, params)
        self.evokedArrays = []
        self.num = 0
        self.times = []
        
    def process(self):
        
        evoked = self.args["Evoked Data"]
        self.evokedArrays.append(evoked)
   
        return
        
    def end(self):
        
        # Get array sizes that I need
        numArrays = len(self.evokedArrays)
        numEvents = len(self.evokedArrays[0])
        numChannels = len(self.evokedArrays[0][0].data)
        numTimes = len(self.evokedArrays[0][0].data[0])
        
        # Imortant information for later
        times = self.evokedArrays[0][0].times
        chNames = self.evokedArrays[0][0].info["ch_names"]
        eventNames = [e.comment for e in self.evokedArrays[0]]
        
        # Setup 4D numpy array to hold data
        data = np.zeros((numEvents, numChannels, numTimes, numArrays))

        # Transform data into required format
        # All subjects for all times for all channels for all events
        for i, evokedArray in enumerate(self.evokedArrays):
            for j, evoked in enumerate(evokedArray):
                for k, channel in enumerate(evoked.data):
                    for l, value in enumerate(channel):
                        data[j, k, l, i] = value
                    
        # data transformation makes getting statistics trivial
        means = np.mean(data, axis = 3)
        stdevs = np.std(data, axis = 3)
        
        # Save data as numpy data structure
        if self.parameters["toggleSaveData"]:
            f = self.parameters["saveGraphData"]
            np.savez(f, chNames = chNames,
                        eventNames = eventNames,
                        times = times,
                        mean = means,
                        std = stdevs)
        
        # Generate graphs for each event type
        for i in range(numEvents):
            fig, ax = plt.subplots()
            for j in range(numChannels):
                ax.fill_between(times * 1000, means[i, j] - stdevs[i, j], means[i, j] + stdevs[i, j])
                ax.plot(times * 1000, means[i, j])
            
            ax.set_xlim([times.min(), times.max() * 1000])
            ax.set_xlabel("Time (ms)")
            ax.set_ylabel("Mean Channel Data")
            ax.set_title("Mean Channel Data for event ID {0}".format(self.evokedArrays[0][i].comment))
            ax.legend(chNames, ncol = 2)
            
            # Save graphs if toggled
            if self.parameters["toggleSaveGraph"]:
                f = self.parameters["saveGraphGraph"]
                type = f.split(".")[-1]
                name = f.split(".")[0]
                f = name + "_{0}.".format(eventNames[i]) + type
                if type == "png":
                    fig.savefig(f, format = "png")
                elif type == "pdf":
                    fig.savefig(f, format = "pdf")
                elif type == "pkl":
                    pickle.dump(fig, open(f, "wb"))
            
            # Show graphs if toggled, close if not
            if self.parameters["toggleShowGraph"]:
                fig.show()
            else:
                plt.close(fig)
        
        return