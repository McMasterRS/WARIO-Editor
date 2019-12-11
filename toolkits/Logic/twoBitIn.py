from pipeline.Node import Node
from extensions.customSettings import CustomSettings
from PyQt5 import QtWidgets

class InputSettings2b(CustomSettings):
    def __init__(self, parent, settings):
        super(InputSettings2b, self).__init__(parent, settings)
        
    def buildUI(self, settings):
        self.layout = QtWidgets.QVBoxLayout()
        
        self.out1 = QtWidgets.QCheckBox("Input 1")
        self.out2 = QtWidgets.QCheckBox("Input 2")
        
        if "out1" in settings.keys():
            self.out1.setChecked(settings["out1"])
            self.out2.setChecked(settings["out2"])
        
        self.layout.addWidget(self.out1)
        self.layout.addWidget(self.out2)
        
        self.setLayout(self.layout)
        
    def genSettings(self):
        settings = {}
        vars = {}
        
        settings["settingsFile"] = self.settings["settingsFile"]
        settings["settingsClass"] = self.settings["settingsClass"]
        
        settings["out1"] = self.out1.isChecked()
        settings["out2"] = self.out2.isChecked()
        
        vars["out1"] = self.out1.isChecked()
        vars["out2"] = self.out2.isChecked()
        
        self.parent.settings = settings
        self.parent.variables = vars
        

class twoBitIn(Node):

    def __init__(self, name, params):   
        super(twoBitIn, self).__init__(name, params)
        
    def process(self):  
        
        return {"Out 1" : self.parameters["out1"], 
                "Out 2" : self.parameters["out2"]}