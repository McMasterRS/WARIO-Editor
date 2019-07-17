from pipeline.Task import Task
import mne

class applyICA(Task):

    def __init__(self, name, params):
        super(applyICA, self).__init__(name, params)
    
    def process(self, solution, epochs):
    
        EpochsICA = solution.apply(epochs.copy())
        
        return EpochsICA