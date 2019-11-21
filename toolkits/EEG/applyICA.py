from pipeline.Node import Node
import mne  
        
class applyICA(Node):

    def __init__(self, name, params):
        super(applyICA, self).__init__(name, params)
    
    def process(self):
    
        solution = self.args["ICA Solution"]
        epochs = self.args["Epoch Data"]    
        exclude = None
        if "Excluded Channels" in self.args.keys():
            exclude = self.args["Excluded Channels"]
        
            
    
        # Make compatable with both epochs/raw
    
        correctedEpochs = solution.apply(inst = epochs,
                                         exclude = exclude)
        
        return {"Epochs" : correctedEpochs}