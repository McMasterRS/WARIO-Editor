from pipeline.Node import Node
import mne
import numpy as np

from tempfile import TemporaryFile

class batchAnalysis(Node):
    def __init__(self, name, params):
        super(batchAnalysis, self).__init__(name, params)
        
        self.latencies = None
        self.amplitudes = None
            
    def process(self):
    
        evokedData = self.args["Evoked Data"]
        
        eventCount = len(evokedData)
        chanCount = evokedData[0].info["nchan"]

        if self.latencies is None:
            self.latencies = np.empty((eventCount, chanCount, 1), dtype=object)
            self.amplitudes = np.empty((eventCount, chanCount, 1), dtype=object)
            
            self.chanNames = evokedData[0].info["ch_names"]
            self.eventNames = [evoked.comment for evoked in evokedData]
        
        # Extract the latencies for each channel for each event
        for i, evoked in enumerate(evokedData):
            for j in range(0, chanCount):
                
                (_, latency, amplitude) = evoked.copy().pick(j).get_peak(return_amplitude = True)
                
                if self.latencies[i, j, 0] == None:
                    self.latencies[i, j, 0] = []
                    self.amplitudes[i, j, 0] = []
                
                self.latencies[i, j, 0].append(latency)
                self.amplitudes[i, j, 0].append(amplitude)
        return
        
    def end(self):
    
        # Converts the lists into properly structured numpy array
        self.latencies = np.array(self.latencies.tolist())
        self.amplitudes = np.array(self.amplitudes.tolist())
    
        # Numpy is great. Calculate all means simultaniously
        meanLatencies = np.mean(self.latencies, axis = 3)
        meanAmplitudes = np.mean(self.amplitudes, axis = 3)
        
        stdevLatencies = np.std(self.latencies, axis = 3)
        stdevAmplitudes = np.std(self.amplitudes, axis = 3)

        outfile = TemporaryFile()
        np.savez(outfile, chNames = self.chanNames, 
                          eventNames = self.eventNames, 
                          meanLatency = meanLatencies.transpose(2, 0, 1)[0], 
                          meanAmplitude = meanAmplitudes.transpose(2, 0, 1)[0],
                          stdLatency = stdevLatencies.transpose(2, 0, 1)[0],
                          stdAmplitude = stdevAmplitudes.transpose(2, 0, 1)[0])
        outfile.seek(0)
        
        npz = np.load(outfile)
       
        return