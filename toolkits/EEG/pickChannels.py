from pipeline.Node import Node
import mne
import sys

class DropEvokedSettings(CustomSettings):
    def __init__(self, parent, settings):
        super(DropEvokedSettings, self).__init__(parent, settings)
        
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

class dropEvokedChannels(Node):

    def __init__(self, name, params):
        super(dropEvokedChannels, self).__init__(name, params)
        
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