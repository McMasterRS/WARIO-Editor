from wario import PipelineThread
from extensions.WalkTree import WalkTree

from PyQt5.QtCore import *
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import uic
from blinker import signal
import sys, os, shutil
import time

# Creates handler instance, displays and starts the given file
# Used when running from commandline
def runPipeline(file):
    threadhandler = ThreadHandler()
    threadhandler.show()
    threadhandler.startPipeline(file)

class ThreadHandler(QtWidgets.QWidget):
    
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        
        self.running = False
        
        # Status signals
        signal("end").connect(self.finishRun)
        signal("crash").connect(self.updateCrash)
        signal('node complete').connect(self.incrimentCount) 
        
        # Load UI and hook to functions
        uiFile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "extensions", "RuntimeWindow.ui")
        uic.loadUi(uiFile, self)
        self.progress.setValue(0)
        self.btStop.clicked.connect(self.stopRun)
        
        # Used for tracking progress
        self.walk = {}
        self.nodeCount = 0
        self.numNodes = 1
        
    def startPipeline(self, file):
    
        # Get the number of nodes to allow for progress tracking
        self.thread = PipelineThread(file)
        self.walk = WalkTree(file)
        self.numNodes = len(self.walk.nodes)
        
        # Update the progress bar 10x per second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateProgress)
        self.timer.start(100)

        # Build temporary files
        if os.path.exists("./wariotmp"):
            shutil.rmtree("./wariotmp/")
        
        os.makedirs("./wariotmp")
    
        # Set the thread's file location
        self.thread.file = file
        
        # Update status text
        self.lbStatus.setText("Running")
        self.updatePalette("#0000FF")
        
        # Start thread
        self.running = True
        self.thread.start()
         
    # Incriments node completion counter
    def incrimentCount(self, sender, **kw):
        self.nodeCount += 1
        
    # Updates progress bar based on number of completed nodes
    def updateProgress(self):
        self.progress.setValue(100 * (self.nodeCount) / self.numNodes)
    
    # Changes status text to the given colour
    def updatePalette(self, color):
        palette = self.lbStatus.palette()
        palette.setColor(palette.Foreground, QtGui.QColor(color))
        self.lbStatus.setPalette(palette)
        
    # Updates the status text when the pipeline crashes
    def updateCrash(self, sender):
        self.lbStatus.setText("Crash - See terminal")
        self.updatePalette("#FF0000")
        self.running = False
        
    # Updates the status text when the pipeline finishes successfully
    def finishRun(self, sender):
        self.lbStatus.setText("Complete")
        self.updatePalette("#00FF00")
        self.running = False
        
    # Kills the thread and updates the status text
    def stopRun(self):
        if self.running == True:
            self.thread.kill()
            self.thread.join()
            
            self.lbStatus.setText("Run Stopped")
            self.updatePalette("#FF0000")
            
            self.running = False
    
if __name__ == "__main__":
    runPipeline(sys.argv[1])
    app.exec_()