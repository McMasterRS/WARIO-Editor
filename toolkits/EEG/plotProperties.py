from pipeline.Node import Node
import mne
import pickle
from nodz.customSettings import CustomSettings
from nodz.customWidgets import saveWidget

from PyQt5 import QtWidgets
from PyQt5 import QtCore

class PlotSettings(CustomSettings):
    def __init__(self, parent, settings):
        super(PlotSettings, self).__init__(parent, settings)
        
    def buildUI(self, settings):
        self.layout = QtWidgets.QFormLayout()
        
        self.showGraph = QtWidgets.QCheckBox("Show Graph")
        if "showGraph" in settings.keys():
            self.showGraph.setChecked(settings["showGraph"])
        else:
            self.showGraph.setChecked(True)
        self.layout.insertRow(-1, self.showGraph, None)
        
        label = QtWidgets.QLabel("File type")
        self.fileType = QtWidgets.QComboBox()
        self.fileType.addItems(["Image", "PDF", "Pickle"])
        if "fileType" in settings.keys():
            self.fileType.setCurrentText(settings["fileType"])
        
        self.saveLoc = saveWidget(self)
        if "saveLoc" in settings.keys():
            self.saveLoc.textbox.setText(settings["saveLoc"])
                    
        self.saveGraph = QtWidgets.QCheckBox("Save Graph")
        self.saveGraph.stateChanged.connect(self.updateSave)
        if "saveGraph" in settings.keys():
            self.saveGraph.setChecked(settings["saveGraph"])
        else:
            self.saveGraph.setChecked(False)
            
        self.layout.insertRow(-1, self.saveGraph, self.saveLoc)
        self.layout.insertRow(-1, label, self.fileType)
        
        self.setLayout(self.layout)
        
    def genSettings(self):
        settings = {}
        vars = {}
        settings["settingsFile"] = self.settings["settingsFile"]
        settings["settingsClass"] = self.settings["settingsClass"]
        
        settings["showGraph"] = self.showGraph.isChecked()
        settings["saveGraph"] = self.saveGraph.isChecked()
        settings["saveLoc"] = self.saveLoc.textbox.text()
        
        vars["showGraph"] = self.showGraph.isChecked()
        if self.saveGraph.isChecked():
            vars["saveGraph"] = self.saveLoc.textbox.text()
        else:
            vars["saveGraph"] = None
        
        self.parent.settings = settings
        self.parent.variables = vars
        
    def updateSave(self, state):
        self.fileType.setEnabled(state)
        self.saveLoc.textbox.setEnabled(state)
        self.saveLoc.button.setEnabled(state)

class plotProperties(Node):
    def __init__(self, name, params):
        super(plotProperties, self).__init__(name, params)

    def process(self):

        inst = self.args["Data"]
        ica = self.args["ICA Solution"]
        
        figs = ica.plot_properties(inst, show = False)
        if self.parameters["showGraph"] == True:
            for fig in figs:
                fig.show()
              
        f = self.paramters["saveGraph"]
        if f is not None:
            if self.parameters["fileType"] == "Image":
                return
            elif self.parameters["fileType"] == "PDF":
                return
            elif self.parameters["fileType"] == "Pickle":
                return
            