from pipeline.Task import Task
import mne

class saveEpochs(Task):

    def __init__(self, name, params):
        super(saveEpochs, self).__init__(name, params)
        
        
    def process(self, epochs):
        epochs.save(self.params["folder"] + '\RAWepochs{}.fif'.format(num))
        return False 