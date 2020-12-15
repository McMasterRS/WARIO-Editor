from wario.CustomWidgets import *
from wario.CustomSettings import *

import collections
from PyQt5 import QtWidgets

# Window that displays node settings based on JSON information
# NOTE: THIS IS EFFECTIVELY UNUSED AND ONLY BEING LEFT TO ENSURE COMPATABILITY
#       UNTIL ALL EXISTING NODES ARE MOVED TO THE NEW SYSTEM (CUSTOM UI WINDOWS)
#       For this reason, I see little reason to do a second pass on commenting

class SettingsItem(CustomSettings):

    def __init__(self, parent, widgets):
        self.nameList = []
        super(SettingsItem, self).__init__(parent, widgets)     
        
    # Initialise the custom UI elements 
    def initCustom(self):
        # find the custom box widget
        for i in range(0, self.layout.rowCount()):
            w = self.layout.itemAt(i,1)
            if isinstance(w, customWidget):
                if w.textbox.text() != "":
                    w.buildCustomUI()
        
    # Populate the settings window    
    def buildUI(self, widgets):
        self.layout = QtWidgets.QFormLayout()
        
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
                
        self.setLayout(self.layout)
                
           
    # Reset the settings window to basic version
    def resetUI(self, custom = False):

        self.nameList = []

        while self.layout.rowCount() > 1:
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