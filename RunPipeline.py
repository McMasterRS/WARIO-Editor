from pipeline.NodeFactory import NodeFactory
from pipeline.NodzInterface import NodzInterface
from pipeline.Pipeline import Pipeline
from pipeline.SignalHandler import SignalHandler
from pipeline.PipelineThread import PipelineThread

from PyQt5.QtCore import *
from PyQt5 import QtWidgets
import traceback
import sys, os, shutil
import pickle
import matplotlib.pyplot as plt
import matplotlib.image as pltimg

import threading

class ThreadHandler(QtWidgets.QWidget):
    pipelineComplete = pyqtSignal(bool)
    
    def __init__(self, signals = None):
        QtWidgets.QWidget.__init__(self)
        
        # Pipeline running variables
        self.signals = signals
        self.signals.end.connect(self.finishRun)
        self.pipelineComplete.connect(self.showPlots)
        
    def startPipeline(self, file):
    
        self.thread = PipelineThread(file, self.signals)
        
        # Build temporary files
        if os.path.exists("./wariotmp"):
            shutil.rmtree("./wariotmp/")
        
        os.makedirs("./wariotmp/plots/")
        os.makedirs("./wariotmp/imgs/")
    
        self.thread.file = file
        self.thread.start()
        
    # Swap from Blinker signal to PyQt5 signal to preserve
    # plots after thread dies.
    def finishRun(self, sender):    
        self.pipelineComplete.emit(True)

    def showPlots(self, val):
        # Show the plots
        for f in os.listdir("./wariotmp/plots/"):
            p = pickle.load(open("./wariotmp/plots/" + f, 'rb'))
            p.show()
        # Show the images as plots
        for f in os.listdir("./wariotmp/imgs"):
            fig = plt.figure()
            img = pltimg.imread("./wariotmp/imgs/"+f)
            imgplot = plt.imshow(img)
            plt.tight_layout()
            plt.axis('off')
            fig.show()
            
        # Clean up temp files
        shutil.rmtree("./wariotmp/")

if __name__ == "__main__":

    runPipeline(sys.argv[1])
    
    app.exec_()