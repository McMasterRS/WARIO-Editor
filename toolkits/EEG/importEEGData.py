from pipeline.Node import Node
import mne 
import numpy as np

class importEEGData(Node):

    def __init__(self, name, params = None):
        super(importEEGData, self).__init__(name, params)
        assert(self.parameters["file"] is not ""), "ERROR: Import Data node has no input file set. Please update the node's settings and re-run"

    def process(self):
  
        data = np.load(self.parameters["file"])
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
        
        return {"Raw" : raw, "Triggers" : trigData}    
        
# ISSUES:
#   - Need a way to set channel names
#   - Need to only pull in eeg channels
#   - Need to confirm this works with multiple input file types
