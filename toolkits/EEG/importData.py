from pipeline.Task import Task
import mne

class importData(Task):

    def __init__(self, params):
        f = params["filename"]
        self.data = mne.io.read_raw_bdf(f)

    def run(self):
        return {"data" : self.data}