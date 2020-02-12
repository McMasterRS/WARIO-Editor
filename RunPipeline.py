from wario import PipelineThread

from PyQt5.QtCore import *
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import uic
from blinker import signal
import sys, os, shutil
import pickle

import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

import mne
import numpy as np

from extensions.WalkTree import WalkTree, TreeItem

#############################################
## Currently designed to go with the EEG   ##
## toolkit. Will replace with generic      ##
## version once this one is working.       ##
#############################################

def runPipeline(file):
    threadhandler = ThreadHandler()
    threadhandler.show()
    threadhandler.startPipeline(file)
    
def getIcon(str):
    return QtWidgets.QWidget().style().standardIcon(getattr(QtWidgets.QStyle,str))

class ThreadHandler(QtWidgets.QWidget):
    pipelineComplete = pyqtSignal(bool)
    
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        
        # Pipeline running variables
        signal("end").connect(self.finishRun)
        signal("crash").connect(self.updateCrash)
        self.pipelineComplete.connect(self.showPlots) 
        
        uic.loadUi('eegWindow.ui', self)
        self.treeWidget.itemClicked.connect(self.showPlot)
        self.treeItem = {}
        self.walk = {}
        self.currentPlot = None
        
    def startPipeline(self, file):
    
        self.thread = PipelineThread(file)
        self.walk = WalkTree(file)
        self.treeWidget.clear()

        # Build temporary files
        if os.path.exists("./wariotmp"):
            shutil.rmtree("./wariotmp/")
        
        os.makedirs("./wariotmp")
    
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
    
    def showPlot(self, item, column):
        
        if item.file is None:
            return
            
        f = pickle.load(open(item.file, 'rb'))
        
        if self.currentPlot is not None:
            plt.close('all')
            
        if f["type"] == "show":
            self.currentPlot = f["data"]
            self.currentPlot.show()
        elif f["type"] == "showMulti":
            for d in f["data"]:
                d.show()
            self.currentPlot = f["data"]
        elif f["type"] == "raw":
            self.currentPlot = f["data"].plot(show = False, scalings = 'auto')
            self.currentPlot.set_size_inches(8, 6)
            self.currentPlot.show()
        elif f["type"] == "sources":
            self.currentPlot = f["ica"].plot_sources(f["data"], show = False)
            self.currentPlot.show()
        elif f["type"] == "customTimes":
            evoked = f["data"]
            max = evoked.times[-1]
            chName, latency, amplitude = evoked.get_peak(return_amplitude = True)
            self.currentPlot = evoked.plot_joint(title = "Event ID {0}".format(evoked.comment),
                  times=np.arange(max / 10.0, max, max / 10.0), show = False)
            self.currentPlot.show()             
        elif f["type"] == "localPeak":
            evoked = f["data"]
            chName, latency, amplitude = evoked.get_peak(return_amplitude = True)
            self.currentPlot = evoked.plot_joint(title = "Local Peaks for event ID {0}".format(evoked.comment), show = False)
            self.currentPlot.show()
            
        elif f["type"] == "peak":
            evoked = f["data"]
            chName, latency, amplitude = evoked.get_peak(return_amplitude = True)
            self.currentPlot = evoked.plot_joint(title = "Peak for event ID {0}".format(evoked.comment), times=latency, show = False)
            self.currentPlot.show()
                
    def showPlots(self, val):

        # Walk through the tree and build the base layout for each output
        for root, directories, files in os.walk(os.path.join(".", "wariotmp")):
            for dir in directories:
                dirRoot = TreeItem(self.treeWidget, [dir], None)
                self.treeItem[dir] = self.walk.buildWidget(dirRoot)
        
                # Add the plots for each output
                for f in os.listdir(os.path.join(".", "wariotmp", dir)): 
                    splitName = f.split(".")
                    node = splitName[0]
                    if len(splitName) == 1:
                        self.treeItem[dir][node].file = os.path.join(".", "wariotmp", dir, f)
                        self.treeItem[dir][node].setIcon(0, getIcon("SP_FileDialogContentsView"))
                    else:
                        self.treeItem[dir][f] = TreeItem(self.treeItem[dir][node], [splitName[1]], None)
                        self.treeItem[dir][f].file = os.path.join(".", "wariotmp", dir, f)
                        self.treeItem[dir][f].setIcon(0, getIcon("SP_FileDialogContentsView"))
            
        for f in os.listdir(os.path.join(".", "wariotmp")): 
            if os.path.isdir(os.path.join(".", "wariotmp", f)):
                continue
                
            if "bulk" not in self.treeItem.keys():
                self.treeItem["bulk"] = TreeItem(self.treeWidget, ["Bulk Results"], None)
                
            item = TreeItem(self.treeItem["bulk"], [f], None)
            item.file = os.path.join(".", "wariotmp", f)
            item.setIcon(0, getIcon("SP_FileDialogContentsView"))

if __name__ == "__main__":

    runPipeline(sys.argv[1])
    
    app.exec_()