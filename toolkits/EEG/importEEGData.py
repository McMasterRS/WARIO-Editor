from pipeline.Node import Node
import mne 

class importEEGData(Node):

    def __init__(self, name, params = None):
        super(importEEGData, self).__init__(name)
        self.parameters = params

        
    def process(self):
  
        data = np.load(self.parameters["file"])
        sfreq = self.parameters["sfreq"])
        
        ch_types = self.parameters["channelTypes"]
        montage = mne.channels.read_montage(kind = self.parameters["montageData"].split(".")[-1], ch_names = None, path = self.parameters["montageData"], transform = True)
        ch_names = montage.ch_names
        
        info = mne.create_info(ch_names = ch_names, sfreq = sfreq, ch_types = ch_types)
        raw = mne.io.RawArray(data, info, first_samp = 0)
        
        raw.set_montage(montage, set_dig=True) 
        raw.pick_types(eeg=True,exclude='bads')
        raw.set_eeg_reference('average',projection=False)
        raw.filter(self.parameters["filter1"], self.parameters["filter2"], n_jobs=1, fir_design='firwin')
        
        return {"Raw" : raw}