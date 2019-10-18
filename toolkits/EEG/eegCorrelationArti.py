from pipeline.Node import Node
import mne


class eegCorrelationArti(Node):
    def __init__(self, name, params):
        super(eegCorrelationArti, self).__init__(name, params)
        
    def process(self):
    
        ica = self.args["ICA Solution"]
        epochs = self.args["Epochs"]
        
        # Repeat this for ECG
        eeg_epochs = mne.preprocessing.create_eeg_epochs(epochs.copy(), reject = None)
        eeg_average = eeg_epochs.average()
        
        # Get ICs that are highly correlated to each EOG channel
        eeg_inds = []
        for name in ch_names['EEG']:
            inds, scores = ica.find_bads_eeg(eeg_epochs, h_freq=10, threshold=self.parameters["threshold"])
            eeg_inds.extend(inds)
            
        eeg_inds = list(set(eeg_inds))
        nInds = len(eeg_inds)
        
        ica.exclude.extend(eeg_inds)
        CleanEEG = ica.apply(epochs.copy())
        
        return {"Corrected Epochs" : epochs, "Corrected ICA" : ica, "Removed Indices" : eeg_inds}
        
        
        
