from pipeline.Node import Node
import mne
import sys

from nodz.customSettings import CustomSettings
from nodz.customWidgets import ExpandingTable
from PyQt5 import QtWidgets, QtCore, QtGui

class DropEvokedChannelsSettings(CustomSettings):
    def __init__(self, parent, settings):
        super(DropEvokedChannelsSettings, self).__init__(parent, settings)
        
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

class dropEvokedChannels(Node):

    def __init__(self, name, params):
        super(dropEvokedChannels, self).__init__(name, params)
        
    def process(self):
        
        evokeds = self.args["Evoked Data"]
        chans = self.parameters["channel"]
        chanNames = evokeds[0].info["ch_names"]
        
        blacklist = []
        if "Channel Indexes" in self.args.keys():
            blacklist = self.args["Channel Indexes"]
            
        for chan in chans:
            c = int(chan)
            if c < len(chanNames) and c >= 0:
                blacklist.append(chanNames[c])
        
        selectedEvokeds = evokeds.copy()
        for evoked in selectedEvokeds:
            evoked.drop_channels(blacklist)
       
        return {"Selected Data" : selectedEvokeds}