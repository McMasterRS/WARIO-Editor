from pipeline.Task import Task
import mne

class fitICA(Task):

    def __init__(self, name, params):
        super(fitICA, self).__init__(name, params)
        
        
    def process(self, data):
        // do magic ICA stuff
        
        return icaSolution