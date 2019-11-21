from pipeline.Node import Node
import mne
import pickle
from extensions.customSettings import CustomSettings
from extensions.customWidgets import GlobalSaveTabs, saveWidget
import matplotlib.pyplot as plt

from PyQt5 import QtWidgets
from PyQt5 import QtCore

class PlotSettings(CustomSettings):
    def __init__(self, parent, settings):
        super(PlotSettings, self).__init__(parent, settings)
        
    def buildUI(self, settings):
        self.layout = QtWidgets.QFormLayout()
        self.layout.setHorizontalSpacing(15)
        
        self.tabLayout = QtWidgets.QVBoxLayout()
        self.tabs = GlobalSaveTabs(["PNG", "PDF", "PKL"], "PNG image (*.png);; PDF (*.pdf);; Pickle (*.pkl)", settings)
        
        self.showGraph = QtWidgets.QCheckBox("Show Graph")
        if "showGraph" in settings.keys():
            self.showGraph.setChecked(settings["showGraph"])
        else:
            self.showGraph.setChecked(True)
                  
        self.saveGraph = QtWidgets.QCheckBox("Save Graph")
        self.saveGraph.stateChanged.connect(self.updateSave)
        if "saveGraph" in settings.keys():
            self.saveGraph.setChecked(settings["saveGraph"])
        else:
            self.saveGraph.setChecked(False)
        self.updateSave(self.saveGraph.isChecked())
            
        self.layout.insertRow(-1, self.showGraph, self.saveGraph)

        self.tabLayout.addItem(self.layout)
        self.tabLayout.addWidget(self.tabs)
        
        self.setLayout(self.tabLayout)
        
    def genSettings(self):
        settings = {}
        vars = {}
        settings["settingsFile"] = self.settings["settingsFile"]
        settings["settingsClass"] = self.settings["settingsClass"]
        
        settings["showGraph"] = self.showGraph.isChecked()
        settings["saveGraph"] = self.saveGraph.isChecked()
        self.tabs.genSettings(settings)
        
        vars["showGraph"] = self.showGraph.isChecked()
        if self.saveGraph.isChecked():
            self.tabs.genVars(vars)
        else:
            vars["saveGraph"] = None
        
        self.parent.settings = settings
        self.parent.variables = vars
        
    def updateGlobals(self, globals):
        self.tabs.updateGlobals(globals)

    def updateSave(self, state):
        self.tabs.setEnabled(state)
        
class plotProperties(Node):
    def __init__(self, name, params):
        super(plotProperties, self).__init__(name, params)

        if self.parameters["saveGraph"] is not None:
            assert(self.parameters["saveGraph"] is not ""), "ERROR: Plot Properties node set to save but no filename has been given. Please update the node settings and re-run"
            
    def process(self):

        inst = self.args["Data"]
        ica = self.args["ICA Solution"]
        
        figs = ica.plot_properties(inst, show = False)

        if self.parameters["saveGraph"] is not None:
            for i, fig in enumerate(figs):
            
                if "globalSaveStart" in self.parameters.keys():
                    f = self.parameters["globalSaveStart"] + self.global_vars["Output Filename"] + self.parameters["globalSaveEnd"]
                else:
                    f = self.parameters["saveGraph"]
                name = f.split(".")[0]
                type = f.split(".")[-1]
                f = name + "_" +  str(i) + "." + type
                if type == "png":
                    fig.savefig(f, format = "png")
                elif type == "pdf":
                    fig.savefig(f, format = "pdf")
                elif type == "pkl":
                    pickle.dump(fig, open(f, "wb"))
                    
        if self.parameters["showGraph"] == True:
            for fig in figs:
                fig.show()
        else:
            for fig in figs:
                plt.close(fig)
            