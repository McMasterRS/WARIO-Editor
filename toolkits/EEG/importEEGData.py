from pipeline.Node import InputNode
import mne

class importEEGData(Task):

    def __init__(self, name, params):
        super(importEEGData, self).__init__(name, params)
        self.data = mne.io.read_raw_bdf(self.parameters["file"])
        
    def process(self):
        print("Running")
        return self.data