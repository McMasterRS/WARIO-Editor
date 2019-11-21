from PyQt5 import QtWidgets
from PyQt5 import QtCore

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import random

class CustomSettings(QtWidgets.QWidget):
    
    def __init__(self, parent, settings):
        super(CustomSettings, self).__init__(None)
        self.parent = parent
        self.settings = settings
        
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.setWindowIcon(self.style().standardIcon(getattr(QtWidgets.QStyle,"SP_TitleBarMenuButton")))
        self.setWindowTitle(self.parent.name + " Settings")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        
        # Build the UI
        self.buildUI(settings)
        
		# Event filter to make sure the main window gets updated settings/
        self.installEventFilter(self)
        
        # Generate starting values for the settings
        self.genSettings()
        
    # Catches window close/loss of focus events
    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.Close:
            self.genSettings()
            event.accept()
        elif event.type() == QtCore.QEvent.WindowDeactivate:
            self.genSettings()
            event.accept()
            
        return False
        
        
    # Build the settings UI
    def buildUI(self, settings):
        return
        
    # Update anything reliant on global vars
    def updateGlobals(self, globals):
        return
        
    # Used in custom nodes. Returns the node attributes
    def getAttribs(self):
        return {"Raw": {
                    "index": -1,
                    "preset": "attr_preset_1",
                    "plug": False,
                    "socket": True,
                    "type": ["rawEEG"]
                },
                "Filtered Raw": {
                    "index": -1,
                    "preset": "attr_preset_1",
                    "plug": True,
                    "socket": False,
                    "type": "rawEEG"   
                }}
    
    # Return the values from each setting type
    def genSettings(self):
        
        # Value of each of the variables for the node. stored as a dict
        varList = {}

        # Information on each settings item to allow for them to be
        # recreated when the file is loaded. Stored as a dict of dicts.
        settingList = {}
    
        self.parent.variables = varList
        self.parent.settings = settingList