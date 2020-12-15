from PyQt5 import QtWidgets
from PyQt5 import QtCore

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import random

class TestSettings(QtWidgets.QWidget):
    
    def __init__(self, parent, settings):
        super(TestSettings, self).__init__(None)
        self.parent = parent
        
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.setWindowIcon(self.style().standardIcon(getattr(QtWidgets.QStyle,"SP_TitleBarMenuButton")))
        self.setWindowTitle("Settings")
        
        # Build the UI
        self.buildUI(settings)
        
		# Event filter to make sure the main window gets updated settings/
        self.installEventFilter(self)
        
    # Catches window close/loss of focus events
    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.Close:
            self.genSettings()
            event.accept()
        elif event.type() == QtCore.QEvent.WindowDeactivate:
            self.genSettings()
            event.accept()
            
        return False
        
    def updateGlobals(self, globals):
        return
        
    # Build the settings UI
    def buildUI(self, settings):
        self.layout = QtWidgets.QHBoxLayout()
        leftLayout = QtWidgets.QFormLayout()
        self.layout.addItem(leftLayout)
        
        btClose = QtWidgets.QPushButton("Close")
        
        leftLayout.insertRow(-1, btClose, None)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        data = [random.random() for i in range(10)]
        self.ax = self.figure.add_subplot(111)
        self.ax.plot(data)
        
        
        self.layout.addWidget(self.canvas)
        
        self.setLayout(self.layout)
        return
        
    # Return the values from each setting type
    def genSettings(self):
        
        # Value of each of the variables for the node. stored as a dict
        varList = []

        # Information on each settings item to allow for them to be
        # recreated when the file is loaded. Stored as a dict of dicts.
        settingList = []
    
        self.parent.settings = settingList
        self.parent.variables = varList