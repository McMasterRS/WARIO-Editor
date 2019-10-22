from pipeline.Node import Node
import mne


class eegCorrelationArti(Node):
    def __init__(self, name, params):
        super(eegCorrelationArti, self).__init__(name, params)
        
    def process(self):
    
        ica = self.args["ICA Solution"]
        epochs = self.args["Epochs"]
        eeg_inds = []
        
        return {"Corrected Epochs" : epochs, "Corrected ICA" : ica, "Removed Indices" : eeg_inds}
        
        
        
