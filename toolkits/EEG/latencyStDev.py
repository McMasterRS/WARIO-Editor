from pipeline.Node import Node
import mne

class latencyStDev(Node):
    def __init__(self, name, params):
        super(latencyStDev, self).__init__(name, params)
        self.latencies = []
            
    def process(self):
    
        evokedData = self.args["Evoked Data"]
        epochLatencies = []
        for evoked in evokedData:

            chName, latency = evoked.get_peak()
            epochLatencies.append(latency)
            
        print(epochLatencies)
        self.latencies.append(epochLatencies)
            
        return
        
    def end(self):
        return