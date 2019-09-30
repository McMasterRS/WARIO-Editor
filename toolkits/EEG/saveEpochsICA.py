from pipeline.Node import Node
import mne

class saveEpochsICA(Node):

    def __init__(self, name, params):
        super(saveEpochsICA, self).__init__(name, params)
        
        
    def process(self, epochsICA):
        epochsICA.save(self.params["folder"] + '\RAWepochs{}.fif'.format(num))
        return False 