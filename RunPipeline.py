from wario import PipelineThread
from extensions.WalkTree import WalkTree

from PyQt5.QtCore import *
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import uic
from blinker import signal
import sys, os, shutil
import time

def runPipeline(file):
    threadhandler = ThreadHandler()
    threadhandler.show()
    threadhandler.startPipeline(file)

class ThreadHandler(QtWidgets.QWidget):
    pipelineComplete = pyqtSignal(bool)
    
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        
        self.running = False
        
        # Pipeline running variables
        signal("end").connect(self.finishRun)
        signal("crash").connect(self.updateCrash)
        signal('node complete').connect(self.incrimentCount) 
        
        uiFile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "extensions", "RuntimeWindow.ui")
        uic.loadUi(uiFile, self)
        self.progress.setValue(0)
        self.btStop.clicked.connect(self.stopRun)
        
        self.walk = {}
        self.nodeCount = 0
        self.numNodes = 1
        
    def startPipeline(self, file):
    
        self.thread = PipelineThread(file)
        self.walk = WalkTree(file)
        self.numNodes = len(self.walk.nodes)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateProgress)
        self.timer.start(50)

        # Build temporary files
        if os.path.exists("./wariotmp"):
            shutil.rmtree("./wariotmp/")
        
        os.makedirs("./wariotmp")
    
        self.thread.file = file
        self.lbStatus.setText("Running")
        self.updatePalette("#0000FF")
        
        self.running = True
        self.thread.start()
         
    def incrimentCount(self, sender, **kw):
        self.nodeCount += 1
        
    def updateProgress(self):
        self.progress.setValue(100 * (self.nodeCount) / self.numNodes)
    
    def updatePalette(self, color):
        palette = self.lbStatus.palette()
        palette.setColor(palette.Foreground, QtGui.QColor(color))
        self.lbStatus.setPalette(palette)
        
    def updateCrash(self, sender):
        self.lbStatus.setText("Crash - See terminal")
        self.updatePalette("#FF0000")
        self.running = False
        
    # Swap from Blinker signal to PyQt5 signal to preserve
    # plots after thread dies.
    def finishRun(self, sender):
        self.lbStatus.setText("Complete")
        self.updatePalette("#00FF00")
        self.running = False
        self.pipelineComplete.emit(True)
        
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