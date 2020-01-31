from wario import PipelineThread

from PyQt5.QtCore import *
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from blinker import signal
import sys, os, shutil
import pickle

import matplotlib.pyplot as plt
import matplotlib.image as pltimg

import mne
import numpy as np

def runPipeline(file):
    threadhandler = ThreadHandler()
    threadhandler.show()
    threadhandler.startPipeline(file)

class ThreadHandler(QtWidgets.QWidget):
    pipelineComplete = pyqtSignal(bool)
    
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        
        # Pipeline running variables
        signal("end").connect(self.finishRun)
        signal("crash").connect(self.updateCrash)
        self.pipelineComplete.connect(self.showPlots) 
        
        self.layout = QtWidgets.QFormLayout()
        lb = QtWidgets.QLabel("Pipeline Status")
        self.lbStatus = QtWidgets.QLabel("")
        self.layout.addRow(lb, self.lbStatus)
        
        self.setLayout(self.layout)
        
    def startPipeline(self, file):
    
        self.thread = PipelineThread(file)
        
        # Build temporary files
        if os.path.exists("./wariotmp"):
            shutil.rmtree("./wariotmp/")
        
        os.makedirs("./wariotmp/plots/")
    
        self.thread.file = file
        self.lbStatus.setText("Running")
        self.updatePalette("#0000FF")
        self.thread.start()
    
    def updatePalette(self, color):
        palette = self.lbStatus.palette()
        palette.setColor(palette.Foreground, QtGui.QColor(color))
        self.lbStatus.setPalette(palette)
        
    def updateCrash(self, sender):
        self.lbStatus.setText("Crash - See terminal")
        self.updatePalette("#FF0000")
        
    # Swap from Blinker signal to PyQt5 signal to preserve
    # plots after thread dies.
    def finishRun(self, sender):
        self.lbStatus.setText("Complete")
        self.updatePalette("#00FF00")
        self.pipelineComplete.emit(True)

    def showPlots(self, val):
        # Show the plots
        for f in os.listdir("./wariotmp/plots/"):
            p = pickle.load(open("./wariotmp/plots/" + f, 'rb'))
            if p["type"] == "show":
                p["data"].show()
                
            elif p["type"] == "raw":
                plot = p["data"].plot(show = False, scalings = 'auto')
                plot.show()
                
            elif p["type"] == "sources":
                plot = p["ica"].plot_sources(p["data"], show = False)
                plot.show()
                
            elif p["type"] == "customTimes":
                evoked = p["data"]
                max = evoked.times[-1]
                chName, latency, amplitude = evoked.get_peak(return_amplitude = True)
                fig = evoked.plot_joint(title = "Event ID {0}".format(evoked.comment),
                      times=np.arange(max / 10.0, max, max / 10.0), show = False)
                fig.show()
                              
            elif p["type"] == "localPeak":
                evoked = p["data"]
                chName, latency, amplitude = evoked.get_peak(return_amplitude = True)
                fig = evoked.plot_joint(title = "Local Peaks for event ID {0}".format(evoked.comment), show = False)
                fig.show()
                
            elif p["type"] == "peak":
                evoked = p["data"]
                chName, latency, amplitude = evoked.get_peak(return_amplitude = True)
                fig = evoked.plot_joint(title = "Peak for event ID {0}".format(evoked.comment), times=latency, show = False)
                fig.show()
            
        # Clean up temp files
        shutil.rmtree("./wariotmp/")

if __name__ == "__main__":

    runPipeline(sys.argv[1])
    
    app.exec_()