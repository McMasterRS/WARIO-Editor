from pipeline.Node import Node
import mne


class ecgCorrelationArti(Node):
    def __init__(self, name, params):
        super(ecgCorrelationArti, self).__init__(name, params)
        
    def process(self):
    
        ica = self.args["ICA Solution"]
        epochs = self.args["Epochs"]
        
        # Repeat this for ECG
        ecg_epochs = mne.preprocessing.create_ecg_epochs(epochs.copy(), reject = None)
        ecg_average = ecg_epochs.average()
        
        # Get ICs that are highly correlated to each EOG channel
        ecg_inds = []
        for name in ch_names['ECG']:
            inds, scores = ica.find_bads_ecg(ecg_epochs, h_freq=10, threshold=self.parameters["threshold"])
            ecg_inds.extend(inds)
            
        ecg_inds = list(set(ecg_inds))
        nInds = len(ecg_inds)
        
        ica.exclude.extend(ecg_inds)
        CleanEEG = ica.apply(epochs.copy())
        
        return {"Corrected Epochs" : epochs, "Corrected ICA" : ica, "Removed Indices" : ecg_inds}
        
        
        
