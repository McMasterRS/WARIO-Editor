from pipeline.Node import Node
from extensions.customSettings import CustomSettings
import mne

from PyQt5 import QtWidgets, QtCore, QtGui

class eogCorrelationArti(Node):
    def __init__(self, name, params):
        super(correlationArti, self).__init__(name, params)
        
    def process(self):
    
        ica = self.args["ICA Solution"]
        epochs = self.args["Epochs"]
        
        # Repeat this for ECG
        eog_epochs = mne.create_eog_epochs(epochs.copy(), reject = None)
        eog_average = eog_epochs.average()
        
        # Get ICs that are highly correlated to each EOG channel
        eog_inds = []
        for name in ch_names['EOG']:
            inds, scores = ica.find_bads_eog(eog_epochs, h_freq=10, threshold=1.5)
            eog_inds.extend(inds)
            
        eog_inds = list(set(eog_inds))
        nInds = len(eog_inds)
        
        ica.exclude.extend(eog_inds)
        CleanEEG = ica.apply(epochs.copy())
        
        return {"Corrected Epochs" : epochs, "Corrected ICA" : ica, "Removed Indices" : eog_inds}
        
        
        # Threshold value for EOG and ECG
            # 1 - inf (float)
        
        
        
