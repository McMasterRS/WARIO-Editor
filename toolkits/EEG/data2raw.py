from pipeline.Node import Node
import mne
from numpy as np

class data2raw(Node):

    # Building a MNE object from a numpy array

    def __init__(self, name, params):
        super(data2raw, self).__init__(name, params)
    
    def process(self):
        data = self.args["Data"]
        
        badchans = []
        
        Raw = mne.io.RawArray(data,info,first_samp=0)
        Raw.set_montage(montage, set_dig=True)
        Raw.info['bads'] = badchans
        Pickchans = mne.pick_types(Raw.info,eeg=True)
        Raw.pick_types(eeg=True,exclude='bads')
        Raw.set_eeg_reference('average',projection=False)
        
        Raw.filter(self.parameters["filter1"], self.parameters["filter2"], n_jobs=1, fir_design='firwin')       
            
        return {"Raw" : Raw, "Pickchans" : Pickchans}
        
        
        
#info
#montage
#badchans
