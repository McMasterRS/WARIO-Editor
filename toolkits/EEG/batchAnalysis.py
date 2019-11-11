from pipeline.Node import Node
from nodz.customSettings import CustomSettings

import mne
import numpy as np
import matplotlib.pyplot as plt

from nodz.customWidgets import LinkedSpinbox, BatchSavePanel, BatchSaveTab

from PyQt5 import QtWidgets
from PyQt5 import QtCore

class BatchAnalysisSettings(CustomSettings):
    def __init__(self, parent, settings):   
        super(BatchAnalysisSettings, self).__init__(parent, settings)
        
    def buildUI(self, settings):
        self.layout = QtWidgets.QVBoxLayout()
        
        self.minTime = LinkedSpinbox()
        self.minTime.setMaximum(10000)
        if "minTime" in settings.keys():
            self.minTime.setValue(settings["minTime"])
        
        self.maxTime = LinkedSpinbox()
        self.maxTime.setMaximum(10000)
        if "maxTime" in settings.keys():
            self.maxTime.setValue(settings["maxTime"])
        
        self.minTime.linkWidgets(self.maxTime, "Higher")
        self.maxTime.linkWidgets(self.minTime, "Lower")
        
        form = QtWidgets.QFormLayout()
        form.setHorizontalSpacing(5)
        form.setVerticalSpacing(5)
        label1 = QtWidgets.QLabel("Minimum Time (ms)")
        label2 = QtWidgets.QLabel("Maximum Time (ms)")
        form.insertRow(-1, label1, self.minTime)
        form.insertRow(-1, label2, self.maxTime)
        
        self.layout.addItem(form)
        
        self.tabs = QtWidgets.QTabWidget()
        
        self.dataSave = BatchSaveTab("Data", "data", settings)
        self.meanSave = BatchSaveTab("Mean", "graph", settings)
        self.stdSave = BatchSaveTab("Std", "graph", settings)
        
        self.tabs.addTab(self.dataSave, "Save Data")
        self.tabs.addTab(self.meanSave, "Save Mean plots")
        self.tabs.addTab(self.stdSave, "Save σ Plots")
        
        self.layout.addWidget(self.tabs)
        
        self.setLayout(self.layout)
        
    def genSettings(self):
    
        settings = {}
        vars = {}
        settings["settingsFile"] = self.settings["settingsFile"]
        settings["settingsClass"] = self.settings["settingsClass"]
        
        settings["minTime"] = self.minTime.value()
        settings["maxTime"] = self.maxTime.value() 
        
        vars["minTime"] = self.minTime.value() / 1000.0
        vars["maxTime"] = self.maxTime.value() / 1000.0
        
        self.dataSave.genSettings(settings, vars)
        self.meanSave.genSettings(settings, vars)
        self.stdSave.genSettings(settings, vars)
    
        self.parent.settings = settings
        self.parent.variables = vars
        
    def updateGlobals(self, globals):
        self.dataSave.updateGlobals(globals)
        self.meanSave.updateGlobals(globals)
        self.stdSave.updateGlobals(globals)
        
class batchAnalysis(Node):
    def __init__(self, name, params):
        super(batchAnalysis, self).__init__(name, params)
        
        self.latencies = None
        self.amplitudes = None
            
    def process(self):
    
        evokedData = self.args["Evoked Data"]
        
        eventCount = len(evokedData)
        chanCount = evokedData[0].info["nchan"]

        if self.latencies is None:
            self.latencies = np.empty((eventCount, chanCount, 1), dtype=object)
            self.amplitudes = np.empty((eventCount, chanCount, 1), dtype=object)
            
            self.chanNames = evokedData[0].info["ch_names"]
            self.eventNames = [evoked.comment for evoked in evokedData]
        
        # Extract the latencies for each channel for each event
        for i, evoked in enumerate(evokedData):
        
            if self.parameters["maxTime"] > evoked.times.max():
                self.parameters["maxTime"] = evoked.times.max()

            for j in range(0, chanCount):
                (_, latency, amplitude) = evoked.copy().pick(j).get_peak(return_amplitude = True, tmin = self.parameters["minTime"], tmax = self.parameters["maxTime"])
                
                if self.latencies[i, j, 0] == None:
                    self.latencies[i, j, 0] = []
                    self.amplitudes[i, j, 0] = []
                
                self.latencies[i, j, 0].append(latency)
                self.amplitudes[i, j, 0].append(amplitude)
        return
        
    def end(self):
    
        # Converts the lists into properly structured numpy array
        self.latencies = np.array(self.latencies.tolist())
        self.amplitudes = np.array(self.amplitudes.tolist())
    
        # Numpy is great. Calculate all means simultaniously
        meanLatencies = np.mean(self.latencies, axis = 3)
        meanAmplitudes = np.mean(self.amplitudes, axis = 3)
        
        stdevLatencies = np.std(self.latencies, axis = 3)
        stdevAmplitudes = np.std(self.amplitudes, axis = 3)
        
        f = self.parameters["saveGraphData"]
                
        if self.parameters["toggleSaveData"]:
            np.savez(f, chNames = self.chanNames, 
                     eventNames = self.eventNames, 
                     meanLatency = meanLatencies.transpose(2, 0, 1)[0], 
                     meanAmplitude = meanAmplitudes.transpose(2, 0, 1)[0],
                     stdLatency = stdevLatencies.transpose(2, 0, 1)[0],
                     stdAmplitude = stdevAmplitudes.transpose(2, 0, 1)[0])
                     
                     
        if self.parameters["toggleSaveMean"]:
        
            f = self.parameters["saveGraphMean"]
        
            fig, ax = plt.subplots()
            width = 0.35
            for i in range(len(meanLatencies)):
                ax.bar(np.arange(len(meanLatencies[i])) + width * i, meanLatencies.transpose(2, 0, 1)[0][i], yerr = stdevLatencies.transpose(2, 0, 1)[0][i], width = width, align = 'center')
                
            ax.set_xticks(np.arange(len(meanLatencies[i])))
            ax.set_xticklabels(self.chanNames)
            ax.set_title("Mean Peak Latencies".format(self.eventNames[i]))
            ax.set_ylabel("Mean Peak Latency")
            ax.set_xlabel("Channel")
            
            fig.tight_layout()
            fig.legend(self.eventNames, title = "Event ID", framealpha = 1)
            
            type = f.split(".")[-1]
            
            if type == "png":
                fig.savefig(f, format = "png")
            elif type == "pdf":
                fig.savefig(f, format = "pdf")
            elif type == "pkl":
                pickle.dump(fig, open(f, "wb"))
        
            if self.parameters["toggleShowMean"]:
                fig.show()
            else:
                plt.close(fig)
            
            
        if self.parameters["toggleSaveStd"]:

            f = self.parameters["saveGraphStd"]
                        
            fig2, ax2 = plt.subplots()
            
            for i in range(len(meanAmplitudes)):
                ax2.bar(np.arange(len(meanAmplitudes[i])) + width * i, meanAmplitudes.transpose(2, 0, 1)[0][i], yerr = stdevAmplitudes.transpose(2, 0, 1)[0][i], width = width, align = 'center')
                
            ax2.set_xticks(np.arange(len(meanAmplitudes[i])))
            ax2.set_xticklabels(self.chanNames)
            ax2.set_title("Mean Peak Amplitudes".format(self.eventNames[i]))
            ax2.set_ylabel("Mean Peak Amplitude")
            ax2.set_xlabel("Channel")
            
            fig2.tight_layout()
            fig2.legend(self.eventNames, title = "Event ID", framealpha = 1)
            
            type = f.split(".")[-1]
            if type == "png":
                fig2.savefig(f, format = "png")
            elif type == "pdf":
                fig2.savefig(f, format = "pdf")
            elif type == "pkl":
                pickle.dump(fig2, open(f, "wb"))
                
            if self.parameters["toggleShowStd"]:
                fig2.show()
            else:
                plt.close(fig2)
       
        return