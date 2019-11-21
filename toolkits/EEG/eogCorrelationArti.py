from pipeline.Node import Node
from extensions.customSettings import CustomSettings
import mne

from PyQt5 import QtWidgets, QtCore, QtGui

class EogCorrelationArtiSettings(CustomSettings):
    def __init__(self, parent, settings):
        super(EogCorrelationArtiSettings, self).__init__(parent, settings)
        
    def buildUI(self, settings):
        self.layout = QtWidgets.QFormLayout()
        
        label = QtWidgets.QLabel("Threshold")
        self.threshold = QtWidgets.QDoubleSpinBox()
        self.threshold.setMinimum(1.0)
        self.threshold.setMaximum(10000000.0)
        if "thresholdValue" in settings.keys():
            self.threshold.setValue(settings["thresholdValue"])
            
        self.layout.insertRow(-1, label, self.threshold)
        
        self.setLayout(self.layout)
        
    def genSettings(self):
        settings = {}
        vars = {}
        settings["settingsFile"] = self.settings["settingsFile"]
        settings["settingsClass"] = self.settings["settingsClass"]
        
        settings["thresholdValue"] = self.threshold.value()
        vars["threshold"] = self.threshold.value()
        
        self.parent.settings = settings
        self.parent.variables = vars

class eogCorrelationArti(Node):
    def __init__(self, name, params):
        super(eogCorrelationArti, self).__init__(name, params)
        
    def process(self):
    
        ica = self.args["ICA Solution"]
        epochs = self.args["Epochs"]
        
        # Repeat this for ECG
        eog_epochs = mne.preprocessing.create_eog_epochs(epochs.copy(), picks = 'eog', reject = None)
        eog_average = eog_epochs.average()
        
        # Get ICs that are highly correlated to each EOG channel
        eog_inds = []
        for name in ch_names['EOG']:
            inds, scores = ica.find_bads_eog(eog_epochs, h_freq=10, threshold=self.parameters["threshold"])
            eog_inds.extend(inds)
            
        eog_inds = list(set(eog_inds))
        nInds = len(eog_inds)
        
        ica.exclude.extend(eog_inds)
        CleanEEG = ica.apply(epochs.copy())
        
        return {"Corrected Epochs" : epochs, "Corrected ICA" : ica, "Removed Indices" : eog_inds}
        
        
        # Threshold value for EOG and ECG
            # 1 - inf (float)
        
        
        
