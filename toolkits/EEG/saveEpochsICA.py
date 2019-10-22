from pipeline.Node import Node
import mne
import sys

class saveEpochsICA(Node):

    def __init__(self, name, params):
        super(saveEpochsICA, self).__init__(name, params)
        assert (self.parameters["file"] is not ""), "ERROR: No filename given in 'Save Epochs ICA' node. Please update the node settings and re-run"
        
        
    def process(self):
        self.args["Epochs ICA"].save(self.parameters["file"], overwrite = True)
        return 