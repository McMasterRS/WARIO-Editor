from pipeline.Node import Node
import mne

class importRawData(Node):

    # Load raw data file

    def __init__(self, name, params):
        super(importRawData, self).__init__(name, params)
    
    def process(self):
        f = self.parameters["Data"] 
        type = f.split(".")[-1]
        raw = []
        
        if type == "bdf":
            raw = mne.io.read_raw_bdf(f)
        elif type == "edf":
            raw = mne.io.read_raw_edf(f)
        elif type == "gdf":
            raw = mne.io.read_raw_gdf(f)
        elif type == "fif":
            raw = mne.io.read_raw_fif(f)
        else:
            raw = mne.io.read_raw_bdf(f)
            
        return {"Raw" : Raw}   
