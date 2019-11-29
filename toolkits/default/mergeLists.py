from pipeline.Node import Node
from extensions.customSettings import CustomSettings

from PyQt5 import QtWidgets
from PyQt5 import QtCore

class MergeListsSettings(CustomSettings):
    def __init__(self, parent, settings):
        super(MergeListsSettings, self).__init__(parent, settings)
        
    def buildUI(self, settings):
        self.layout = QtWidgets.QHBoxLayout()
        
        self.delDuplicates = QtWidgets.QCheckBox("Delete Duplicates")
        self.layout.addWidget(self.delDuplicates)
        if "deleteDuplicates" in settings.keys():
            self.delDuplicates.setChecked(settings["deleteDuplicates"])
        
        self.setLayout(self.layout)
        
    def genSettings(self):
        settings = {}
        vars = {}
        
        settings["settingsFile"] = self.settings["settingsFile"]
        settings["settingsClass"] = self.settings["settingsClass"]
        
        settings["deleteDuplicates"] = self.delDuplicates.isChecked()
        vars["deleteDuplicates"] = self.delDuplicates.isChecked()
        
        self.parent.settings = settings
        self.parent.variables = vars
        
    def getAttribs(self):
        attribs = {
                    "List 1": {
                        "index": -1,
                        "preset": "attr_preset_1",
                        "plug": False,
                        "socket": True,
                        "type": "list"
                    },
                    "List2": {
                        "index": -1,
                        "preset": "attr_preset_1",
                        "plug": False,
                        "socket": True,
                        "type": "list"
                    },
                    "List 3": {
                        "index": -1,
                        "preset": "attr_preset_1",
                        "plug": False,
                        "socket": True,
                        "type": "list"
                    },
                    "List 4": {
                        "index": -1,
                        "preset": "attr_preset_1",
                        "plug": False,
                        "socket": True,
                        "type": "list"
                    },
                    "Merged List": {
                        "index": -1,
                        "preset": "attr_preset_1",
                        "plug": True,
                        "socket": False,
                        "type": "list"
                    }
                }
                
        return attribs

class mergeLists(Node):
    
    def __init__(self, name, params):
        super(mergeLists, self).__init__(name, params)
    
    def process(self):
        
        list = []
        
        # Check each input attribute for a list
        # Allows for any number of the 4 nodes to be used
        for i in range(4):
            if "List {0}".format(i+1) in self.args.keys():
                list.append(self.args["List {0}".format(i+1)])
                
        # Delete duplicates if the setting is checked
        if self.parameters["deleteDuplicates"] == True:
            list = list(dict.fromkeys(list))
                
        return {"Merged List" : list}
    