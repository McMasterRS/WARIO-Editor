from wario import PipelineThread

from PyQt5.QtCore import *
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import uic
from blinker import signal
import sys, os, shutil

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
        
        os.makedirs("./wariotmp")
    
        self.thread.file = file
        self.lbStatus.setText("Running")
        self.updatePalette("#0000FF")
        
        self.running = True
        self.thread.start()
    
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
    
if __name__ == "__main__":

    runPipeline(sys.argv[1])
    
    app.exec_()