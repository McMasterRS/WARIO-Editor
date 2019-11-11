from pipeline.Node import Node
import mne
import sys

from nodz.customSettings import CustomSettings
from nodz.customWidgets import ExpandingTable
from PyQt5 import QtWidgets, QtCore, QtGui

class DropEpochChannelsSettings(CustomSettings):
    def __init__(self, parent, settings):
        super(DropEpochChannelsSettings, self).__init__(parent, settings)
        
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
        
        self.table.getSettings("channel", vars, settings)
        
        self.parent.settings = settings
        self.parent.variables = vars

class dropEpochChannels(Node):

    def __init__(self, name, params):
        super(dropEpochChannels, self).__init__(name, params)
        
    def process(self):
        
        epochs = self.args["Epoch Data"]
        chans = self.parameters["channel"]
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