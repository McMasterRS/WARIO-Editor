from pipeline.NodeFactory import NodeFactory
from pipeline.NodzInterface import NodzInterface
from pipeline.Pipeline import Pipeline
from PyQt5.QtCore import *
from PyQt5 import QtWidgets
import traceback
import sys, os, shutil
import pickle
import matplotlib.pyplot as plt
import matplotlib.image as pltimg
from queue import Queue

import threading

def runPipeline(file):
    
    handler = ThreadHandler(file)
    handler.show()
    handler.startPipeline()
    

class ThreadHandler(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        
        # Pipeline running variables
        self.queue = Queue()
        self.thread = PipelineThread(self.queue)
        self.thread.pipelineComplete.connect(self.showPlots)
        
    def startPipeline(self, file):
        # Build temporary files
        if os.path.exists("./wariotmp"):
            shutil.rmtree("./wariotmp/")
        
        os.makedirs("./wariotmp/plots/")
        os.makedirs("./wariotmp/imgs/")
    
        self.thread.file = file
        self.thread.start()

    def showPlots(self, val):
        for f in os.listdir("./wariotmp/plots/"):
            p = pickle.load(open("./wariotmp/plots/" + f, 'rb'))
            p.show()
            
        for f in os.listdir("./wariotmp/imgs"):
            fig = plt.figure()
            img = pltimg.imread("./wariotmp/imgs/"+f)
            imgplot = plt.imshow(img)
            plt.tight_layout()
            plt.axis('off')
            fig.show()
            
        # Clean up temp files
        shutil.rmtree("./wariotmp/")


class PipelineThread(QThread):
    pipelineComplete = pyqtSignal(bool)

    def __init__(self, queue):
        QThread.__init__(self)
        
        self.queue = queue
        self.file = []

        
    def run(self):
        
        try:
            # Extract relevant info from the JSON
            nodes, connections, globals = NodzInterface.load(self.file)

            # Build the pipeline graph
            pipeline = Pipeline(global_vars = globals)

            for node in nodes:
                pipeline.add(node[1])
                
            for conn in connections:
                pipeline.connect(parent = conn[0], child = conn[1])

            pipeline.start()
            
        # Catches any runtime errors and prints to console
        # Lets you debug the pipeline nodes if they crash
        except Exception:
            traceback.print_exc()
            
        self.pipelineComplete.emit(True)
        
    def updateUI(self):
        return
     
if __name__ == "__main__":

    runPipeline(sys.argv[1])
    
    app.exec_()