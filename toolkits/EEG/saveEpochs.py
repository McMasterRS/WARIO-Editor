from pipeline.Node import Node
import mne

class saveEpochs(Node):

    def __init__(self, name, params):
        super(saveEpochs, self).__init__(name, params)
        
        
    def process(self):
    
        epochs = self.args["Epoch Data"]
        epochs.save(self.params["folder"] + '\RAWepochs{0}.fif'.format(num))
        
        return