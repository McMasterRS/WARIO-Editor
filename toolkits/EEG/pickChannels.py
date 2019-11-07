from pipeline.Node import Node
import mne
import sys

class pickChannels(Node):

    def __init__(self, name, params):
        super(pickChannels, self).__init__(name, params)
        
    def process(self):
        evoked = self.args["Evoked Data"]
        chNames = evoked.info["ch_names"]
        
        if "Channels" in self.args.keys():
            chanPicks = self.args.keys("Channels")
        else:
            
        
        picks = evoked.pick_channels(chNames)
        return {"Selected Evoked Data" : picks}