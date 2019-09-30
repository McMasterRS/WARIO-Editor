from pipeline.Node import Node
import mne

class fitICA(Node):

    def __init__(self, name, params):
        super(fitICA, self).__init__(name, params)
        
        
    def process(self):
        # do magic ICA stuff
        
        data = self.parameters["Raw"]    
        
        return {"ICA Solution" : icaSolution}