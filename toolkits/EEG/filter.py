from pipeline.Node import Node
import mne 
import numpy as np
from nodz.customSettings import CustomSettings
from PyQt5 import QtWidgets, QtCore, QtGui

class FilterSettings(CustomSettings):
    def __init__(self, parent, settings):
        super(FilterSettings, self).__init__(parent, settings)

    # Build the settings UI
    def buildUI(self, settings):
    
        self.layout = QtWidgets.QVBoxLayout()
        self.tabs = QtWidgets.QTabWidget()
        
        self.lowPass = QtWidgets.QWidget()
        self.highPass = QtWidgets.QWidget()
        self.bandPass = QtWidgets.QWidget()
        self.notch = QtWidgets.QWidget()
        
        self.lpLayout = QtWidgets.QFormLayout()
        self.hpLayout = QtWidgets.QFormLayout()
        self.bpLayout = QtWidgets.QFormLayout()
        self.nLayout = QtWidgets.QFormLayout()
 
        # Low pass filter
        
        self.lpCutoff = QtWidgets.QSpinBox()
        self.lpCutoff.setMaximum(100000)
        label = QtWidgets.QLabel("Lower band edge")
        if "lpCutoff" in settings.keys():
            self.lpCutoff.setValue(settings["lpCutoff"])
        self.lpLayout.insertRow(-1, label, self.lpCutoff)
        
        # High pass filter
        
        self.hpCutoff = QtWidgets.QSpinBox()
        self.hpCutoff.setMaximum(100000)
        label = QtWidgets.QLabel("Higher band edge")
        if "hpCutoff" in settings.keys():
            self.hpCutoff.setValue(settings["hpCutoff"])
        self.hpLayout.insertRow(-1, label, self.hpCutoff)
        
        # Band filter
        
        self.bandLowCutoff = QtWidgets.QSpinBox()
        self.bandLowCutoff.setMaximum(100000)
        label = QtWidgets.QLabel("Lower band edge")
        if "bandLowCutoff" in settings.keys():
            self.bandLowCutoff.setValue(settings["bandLowCutoff"])
        self.bpLayout.insertRow(-1, label, self.bandLowCutoff)
        
        self.bandHighCutoff = QtWidgets.QSpinBox()
        self.bandHighCutoff.setMaximum(100000)
        label = QtWidgets.QLabel("Higher band edge")
        if "bandHighCutoff" in settings.keys():
            self.bandHighCutoff.setValue(settings["bandHighCutoff"])
        self.bpLayout.insertRow(-1, label, self.bandHighCutoff)
        
        # Notch filter
        
        self.notchFreq = QtWidgets.QSpinBox()
        self.notchFreq.setMaximum(100000)
        label = QtWidgets.QLabel("Notch frequency")
        if "notchFreq" in settings.keys():
            self.notchFreq.setValue(settings["notchFreq"])
        self.nLayout.insertRow(-1, label, self.notchFreq)
        
        self.notchWidth = QtWidgets.QSpinBox()
        self.notchWidth.setMaximum(100000)
        label = QtWidgets.QLabel("Notch width")
        if "notchWidth" in settings.keys():
            self.notchWidth.setValue(settings["notchWidth"])
        self.nLayout.insertRow(-1, label, self.notchWidth)
       
        # Settings items universal to all filter types
        self.form = QtWidgets.QFormLayout()
        self.form.setSpacing(5)
            
        phaseLabel = QtWidgets.QLabel("Phase")
        self.phase = QtWidgets.QComboBox()
        self.phase.addItems(["Zero", "Zero-Double", "Minimum"])
        if "phase" in settings.keys():
            self.phase.setCurrentText(settings["phase"])
        
        firWindowLabel = QtWidgets.QLabel("FIR Window")
        self.firWindow = QtWidgets.QComboBox()
        self.firWindow.addItems(["Hamming", "Hann", "Blackman"])
        if "firWindow" in settings.keys():
            self.firWindow.setCurrentText(settings["firWindow"])
        
        methodLabel = QtWidgets.QLabel("Method")
        self.method = QtWidgets.QComboBox()
        self.method.addItems(["FIR"])
        self.method.currentIndexChanged.connect(self.updateMethod)
        if "method" in settings.keys():
            self.method.setCurrentText(settings["method"])
            
        self.form.insertRow(-1, methodLabel, self.method)
        self.form.insertRow(-1, phaseLabel, self.phase)
        self.form.insertRow(-1, firWindowLabel, self.firWindow)
        
        self.lowPass.setLayout(self.lpLayout)
        self.highPass.setLayout(self.hpLayout)
        self.bandPass.setLayout(self.bpLayout)
        self.notch.setLayout(self.nLayout)
        
        self.tabs.addTab(self.lowPass, "Low Pass")
        self.tabs.addTab(self.highPass, "High Pass")
        self.tabs.addTab(self.bandPass, "Band Pass")
        self.tabs.addTab(self.notch, "Notch")
        self.tabs.currentChanged.connect(self.updateName)
        self.resize(360,150)
        
        if "tab" in settings.keys():
            self.tabs.setCurrentIndex(settings["tab"])
        
        self.layout.addWidget(self.tabs)
        self.layout.addItem(self.form)
        self.setLayout(self.layout)
        
    def genSettings(self):
        
        varList = {}
        settingList = {}
        
        settingList["lpCutoff"] = self.lpCutoff.value()
        settingList["hpCutoff"] = self.hpCutoff.value()
        settingList["bandLowCutoff"] = self.bandLowCutoff.value()
        settingList["bandHighCutoff"] = self.bandHighCutoff.value()
        settingList["notchFreq"] = self.notchFreq.value()
        settingList["notchWidth"] = self.notchWidth.value()
        settingList["method"] = self.method.currentText()
        settingList["phase"] = self.phase.currentText()
        settingList["firWindow"] = self.firWindow.currentText()
        settingList["tab"] = self.tabs.currentIndex()
        
        varList = settingList.copy()
        settingList["settingsFile"] = self.settings["settingsFile"]
        settingList["settingsClass"] = self.settings["settingsClass"]
        
        self.parent.variables = varList
        self.parent.settings = settingList
        
    def updateMethod(self, index):
        if index != 0:
            self.phase.setDisabled(True)
            self.firWindow.setDisabled(True)
        else:
            self.phase.setDisabled(False)
            self.firWindow.setDisabled(False)
            
    def updateName(self, index):
        print("Test")
        names = ["Low Pass", "High Pass", "Band Pass", "Notch"]
        self.parent.name = names[index] + " Filter"
        
class filter(Node):

    def __init__(self, name, params = None):
        super(filter, self).__init__(name)
        self.parameters = params
    
    def process(self):
    
        tab = self.parameters["tab"]
        raw = self.args["Raw"]
        
        # If not a notch filter
        if tab != 3:
        
            l_freq = None
            h_freq = None
            
            # Low pass
            if tab == 0:
                h_freq = self.parameters["lpCutoff"]
            # High pass
            elif tab == 1:
                l_freq = self.parameters["hpCutoff"]
            # Band pass
            elif tab == 2:
                l_freq = self.parameters["bandLowCutoff"]
                h_freq = self.parameters["bandHighCutoff"]

            # FIXME - IIR not working
            raw.filter(l_freq = l_freq,
                       h_freq = h_freq,
                       picks = ['meg', 'eeg'],
                       n_jobs = 1,
                       method = self.parameters["method"].lower(),
                       phase = self.parameters["phase"].lower(),
                       fir_window = self.parameters["firWindow"].lower(),
                       skip_by_annotation = ('edge', 'bad_acq_skip') # table with option for more?
                       )
        # Notch filter
        else:
            raw.notch_filter(freqs = self.parameters["notchFreq"],
                             picks = ['meg', 'eeg'],
                             notch_widths = self.parameters["notchWidth"],
                             n_jobs = 1,
                             method = self.parameters["method"].lower(),
                             phase = self.parameters["phase"].lower(),
                             fir_window = self.parameters["firWindow"].lower()
                             )
        
        return {"Filtered Raw" : raw}