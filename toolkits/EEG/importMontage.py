from pipeline.Node import Node
import mne

class importMontage(Node):

    def __init__(self, name, params):
        super(importMontage, self).__init__(name)
        self.parameters = params
        
    def process(self):
        file = self.parameters["file"].split("/")
        montageFile = file[-1].split(".")[0]
        filepath = "/".join(file[:-1])
        
        data = mne.channels.read_montage(kind=montageFile,ch_names=None,path=filepath,transform=True)
        
        return {"Montage" : data}