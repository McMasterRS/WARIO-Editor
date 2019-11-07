from pipeline.Node import Node
import mne 
import numpy as np
import os

from nodz.customSettings import CustomSettings
from nodz.customWidgets import ExpandingTable

from PyQt5 import QtWidgets, QtCore, QtGui

class ImportDataSettings(CustomSettings):
    def __init__(self, parent, settings):
        super(ImportDataSettings, self).__init__(parent, settings)
        
    def buildUI(self, settings):
    
        self.layout = QtWidgets.QVBoxLayout()
        
        self.table = ExpandingTable("channel", settings)
        self.table.setHorizontalHeaderLabels(["Channel #s"])
        
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)
        
    def genSettings(self):
        settings = {}
        vars = {}
        settings["settingsFile"] = self.settings["settingsFile"]
        settings["settingsClass"] = self.settings["settingsClass"]
        
        self.table.getSettings(settings, vars)
        
        self.parent.settings = settings
        self.parent.variables = vars
        
class placeholderClass(Node):
    def __init__(self, name, params = None):
        super(placeholderClass, self).__init__(name, params)
        
    def process(self):
        
        evokeds = self.args["Evoked Data"]
        chans = self.parameters["channelValues"]
        chanNames = evokeds[0].info["chan_names"]
        
        if "Channel Indexes" in self.args.keys():
            blacklist = self.args["Channel Indexes"]
            
        for chan in chans:
            c = int(chan)
            if c < len(chanNames) and c >= 0:
                blacklist.append(chanNames[c])
        
        selectedEvokeds = evokeds.copy()
        for evoked in selectedEvokeds:
            evoked.drop_channels(blacklist)
            
        print(selectedEvokeds[0].info)
       
        return {"Selected Data" : selectedEvokeds}
        
    def process(self):
        
        epochs = self.args["Epoch Data"]
        chans = self.parameters["channelValues"]
        chanNames = epochs.ch_names
        
        blacklist = []
        
        if "Channel Indexes" in self.args.keys():
            blacklist = self.args["Channel Indexes"]
        for chan in chans:
            c = int(chan)
            if c < len(chanNames) and c >= 0:
                blacklist.append(chanNames[c])
                
        selectedEpochs = epochs.copy()
        selectedEpochs.drop_channels(blacklist)
        
        return {"Selected Data" : selectedEpochs}
        
        
class importEEGData(Node):

    def __init__(self, name, params = None):
        super(importEEGData, self).__init__(name, params)
        assert(self.parameters["file"] is not ""), "ERROR: Import Data node has no input file set. Please update the node's settings and re-run"
        
        self.parameters["updateGlobal"] = True
        self.parameters["files"] = ["C:/Users/Tom/Documents/Github/nodz/saves/Data/MWEEG_Subject_0.npz"]# "C:/Users/mudwayt/Documents/GitHub/nodz/saves/Data/MWEEG_Subject_9.npz"]
        self.parameters["makeFolders"] = True

    def process(self):
  
        currentFile = self.parameters["files"][0]
        data = np.load(currentFile)
        print(data)
        
        # Update the global filename variable with each new file
        # Useful for batch jobs where you want each dataset to output results with matching names
        if self.parameters["updateGlobal"] == True:
            self.global_vars["Output Filename"] = os.path.splitext(os.path.split(currentFile)[1])[0]

        # Save output from each data file in its own folder
        if self.parameters["makeFolders"] == True:
            dir = os.path.join(self.global_vars["Output Folder"].getVal(), self.global_vars["Output Filename"])
            self.global_vars["Output Filename"] = os.path.join(self.global_vars["Output Filename"], self.global_vars["Output Filename"])
            if not os.path.isdir(dir):
                os.mkdir(dir)
              
        sfreq = self.parameters["sfreq"]
        
        trigTimes = data["SampleTime"][data["TriggerTime"] != 0.][:13] ## FIXME
        trigData = [data["TriggerValues"], trigTimes]
        
        filenameNoExt = self.parameters["montageData"].split(".")[0]
        file = filenameNoExt.split("/")[-1]
        folder = filenameNoExt[:-1*len(file)]

        montage = mne.channels.read_montage(kind = file, ch_names = None, path = folder, transform = True)
        ch_names = montage.ch_names
        
        ch_types = open(self.parameters["channelTypes"], 'r').read().split(",")

        info = mne.create_info(ch_names = ch_names[-16:], sfreq = sfreq, ch_types = ch_types)
        raw = mne.io.RawArray(data["EEG"], info, first_samp = 0)
        
        raw.set_montage(montage, set_dig=True) 
        raw.pick_types(eeg=True,exclude='bads')
        raw.set_eeg_reference('average',projection=False)
        
        # Check if more data needs to be ran
        self.parameters["files"].pop(0)
        self.done = not len(self.parameters["files"]) > 0
            
        return {"Raw" : raw, "Triggers" : trigData}    
        
# ISSUES:
#   - Need to only pull in eeg channels
#   - Need to confirm this works with multiple input file types
