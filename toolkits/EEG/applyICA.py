from pipeline.Node import Node
import mne

class applyICA(Node):

    def __init__(self, name, params):
        super(applyICA, self).__init__(name, params)
    
    def process(self):
    
        solution = self.args["ICA Solution"]
        epochs = self.args["Epoch Data"]
    
        # Make compatable with both epochs/raw
    
        correctedEpochs = solution.apply(epochs)
        
        # Exclude
        
        return {"Epochs" : correctedEpochs}