from pipeline.Node import Node
from extensions.customSettings import CustomSettings
from PyQt5 import QtWidgets

class InputSettings(CustomSettings):
    def __init__(self, parent, settings):
        super(InputSettings, self).__init__(parent, settings)
        
    def buildUI(self, settings):
        self.layout = QtWidgets.QVBoxLayout()
        
        self.out1 = QtWidgets.QCheckBox("Input 1")
        self.out2 = QtWidgets.QCheckBox("Input 2")
        self.out3 = QtWidgets.QCheckBox("Input 3")
        self.out4 = QtWidgets.QCheckBox("Input 4")
        
        if "out1" in settings.keys():
            self.out1.setChecked(settings["out1"])
            self.out2.setChecked(settings["out2"])
            self.out3.setChecked(settings["out3"])
            self.out4.setChecked(settings["out4"])
        
        self.layout.addWidget(self.out1)
        self.layout.addWidget(self.out2)
        self.layout.addWidget(self.out3)
        self.layout.addWidget(self.out4)
        
        self.setLayout(self.layout)
        
    def genSettings(self):
        settings = {}
        vars = {}
        
        settings["settingsFile"] = self.settings["settingsFile"]
        settings["settingsClass"] = self.settings["settingsClass"]
        
        settings["out1"] = self.out1.isChecked()
        settings["out2"] = self.out2.isChecked()
        settings["out3"] = self.out3.isChecked()
        settings["out4"] = self.out4.isChecked()
        
        vars["out1"] = self.out1.isChecked()
        vars["out2"] = self.out2.isChecked()
        vars["out3"] = self.out3.isChecked()
        vars["out4"] = self.out4.isChecked()
        
        self.parent.settings = settings
        self.parent.variables = vars
        

class fourBitIn(Node):

    def __init__(self, name, params):   
        super(fourBitIn, self).__init__(name, params)
        
    def process(self):
        
        return {"Out 1" : self.parameters["out1"], 
                "Out 2" : self.parameters["out2"], 
                "Out 3" : self.parameters["out3"], 
                "Out 4" : self.parameters["out4"]}