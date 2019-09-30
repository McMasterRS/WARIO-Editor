import nodz.nodz_utils as utils
from nodz.customWidgets import *

import json
import collections

from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import uic

# Window that displays node settings
class settingsItem(QtWidgets.QWidget):

    def __init__(self, parent, widgets):
        super(settingsItem, self).__init__(None)
        self.parent = parent
        self.nameList = []
        
        self.layout = QtWidgets.QFormLayout()
        self.buildUI(widgets)
        self.setLayout(self.layout)
        
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.setWindowIcon(self.style().standardIcon(getattr(QtWidgets.QStyle,"SP_TitleBarMenuButton")))
        self.setWindowTitle("Settings")
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.installEventFilter(self)

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
        
    # Initialise the custom UI elements 
    def initCustom(self):
        # find the custom box widget
        for i in range(0, self.layout.rowCount()):
            w = self.layout.itemAt(i,1)
            if isinstance(w, customWidget):
                if w.textbox.text() != "":
                    w.buildCustomUI()
                
                
        
    # Populate the settings window    
    def buildUI(self, widgets, custom = False):
        # If not building the custom node UI add the rename textbox
        # to the top of the settings menu
        if custom == False:
            label = QtWidgets.QLabel("Node Name")
            widget = self.genWidget("textbox", {'text': self.parent.name})
            self.layout.insertRow(-1, label, widget)

        # Loop through all the widgets in the json file and
        # add them to the settings menu
        for i in widgets:
            # Give error message if any essential info is missing
            errors = []
            if "text" not in widgets[i]: errors.append("text")
            if "type" not in widgets[i]: errors.append("type")
            if "params" not in widgets[i]: errors.append("params")
            if len(errors) > 0:
                QtWidgets.QMessageBox.critical(self, "ERROR", "'{0}' node setting {1} missing values {2}".format(self.parent.name, i, errors))
                continue
            
            self.nameList.append(i)
            label = QtWidgets.QLabel(widgets[i]["text"])
            widget = self.genWidget(widgets[i]["type"], widgets[i]["params"])
            self.layout.insertRow(-1, label, widget)
            
            # Cancel building the UI after a custom node
            # If loading/duplicating, the generation code in the custom box
            # handles the rest of the UI generation but we need to make sure
            # it has the values held in the duplicated/loaded noded
            if widgets[i]["type"] == "custombox":
                widget.tempSettings = widgets
                break
                
           
    # Reset the settings window to basic version
    def resetUI(self, custom = False):

        start = 1
        if custom:
            start = 2
            self.nameList = [self.nameList[0]]
        else:
            self.nameList = []

        while self.layout.rowCount() > start:
            self.layout.removeRow(self.layout.rowCount() - 1)
            
    # Generate the settings row based on its defined widget
    def genWidget(self, widget, params):
        
        if widget == "textbox":
            w = QtWidgets.QLineEdit()
            if "text" in params: w.setText(params["text"]) 
            
        elif widget == "spinbox":
            w = QtWidgets.QSpinBox()
            if "minimum" in params: w.setMinimum(params["minimum"]) 
            if "maximum" in params: w.setMaximum(params["maximum"]) 
            if "value" in params: w.setValue(params["value"]) 
            
        elif widget == "checkbox":
            w = QtWidgets.QCheckBox()
            if "checked" in params: w.setChecked(params["checked"]) 
            
        elif widget == "loadbox":
            w = loadWidget(self)
            if "text" in params: w.textbox.setText(params["text"]) 
            
        elif widget == "custombox":
            w = customWidget(self)
            if "text" in params: 
                w.textbox.setText(params["text"])
            
        elif widget == "combobox":
            w = QtWidgets.QComboBox()
            
        elif widget == "globalbox":
            w = GlobalNodeComboBox(self.parent, params["loaded"], params["value"])
            
        else:
            QtWidgets.QMessageBox.critical(self, "ERROR", "Unrecognised setting type '{0}' for node {1}".format(widget, self.parent.name))
            return None
            
        return w

    # Return the values from each setting type
    def genSettings(self):
    
        # Update the name of the node
        self.parent.name = self.layout.itemAt(0,1).widget().text()
        
        # Ordered dicts so that we get the same setting order when we load
        data = collections.OrderedDict()
        vars = collections.OrderedDict()
        
        # Loop through rows and extract dict of setting data
        # for saving/duplicating
        for i in range(1, self.layout.rowCount()):
            setting = {'text' : "", 'type' : "", 'params' : {}}
            setting['text'] = self.layout.itemAt(i,0).widget().text()
            
            var = []
            
            w = self.layout.itemAt(i,1)
            if w is None:
                continue
            
            # Save appropriate details based on the type of the widget
            if isinstance(w, customWidget):
                setting['type'] = 'custombox'
                setting['params'] = {'text' : w.textbox.text()}
                var = w.textbox.text() 
            elif isinstance(w, loadWidget):  
                setting['type'] = "loadbox"
                setting['params'] = {'text' : w.textbox.text()}
                var = w.textbox.text()
            elif isinstance(w.widget(), GlobalNodeComboBox):
                setting['type']  = "globalbox"
                setting['params'] = {'value' : w.widget().currentText(), 'loaded' : True}
            elif isinstance(w.widget(), QtWidgets.QLineEdit):
                setting['type'] = "textbox"
                setting['params'] = {'text' : w.widget().text()}
                var = w.widget().text()
            elif isinstance(w.widget(), QtWidgets.QCheckBox):
                setting['type'] = "checkbox"
                setting['params']  = {'checked' : w.widget().isChecked()}
                var = w.widget().isChecked()
            elif isinstance(w.widget(), QtWidgets.QSpinBox):
                setting['type'] = "spinbox"
                setting['params'] = {'minimum' : w.widget().minimum(), 'maximum' : w.widget().maximum(), 'value' : w.widget().value()}
                var = w.widget().value()
            elif isinstance(w.widget(), QtWidgets.QComboBox):
                setting['type'] = "combobox"
                setting['params'] = {'selected' : w.widget().currentID()}

            data[self.nameList[i-1]] = setting
            vars[self.nameList[i-1]] = var
            
        self.parent.settings = data
        self.parent.variables = vars