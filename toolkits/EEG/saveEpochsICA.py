from pipeline.Node import Node
import mne
import sys

class saveEpochsICA(Node):

    def __init__(self, name, params):
        super(saveEpochsICA, self).__init__(name, params)
        assert (self.parameters["file"] is not ""), "ERROR: No filename given in 'Save Epochs ICA' node. Please update the node settings and re-run"
        
        
    def process(self):
    
        if "globalSaveStart" in self.parameters.keys():
            f = self.parameters["globalSaveStart"] + self.global_vars["Output Filename"] + self.parameters["globalSaveEnd"]
        else:
            f = self.parameters["file"]
                
        self.args["Epochs ICA"].save(f, overwrite = True)
        return 