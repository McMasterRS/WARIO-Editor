from pipeline.Node import Node
from nodz.customSettings import CustomSettings
from nodz.customWidgets import LinkedCheckbox, LinkedSpinbox
import mne

from PyQt5 import QtWidgets, QtCore, QtGui

class CriterionTable(QtWidgets.QTableWidget):
    def __init__(self, settings):
        super(CriterionTable, self).__init__(3, 2)
        
        names = ["Skew", "Kurt", "Var"]
        self.setHorizontalHeaderLabels(["Type", "Value"])
        self.setVerticalHeaderLabels(names) 
        
        for i in range(self.rowCount()):
            combobox = QtWidgets.QComboBox()
            combobox.addItems(["None", "Int", "Float"])
            combobox.currentIndexChanged.connect(lambda index, row=i: self.updateTypes(index, row))
            textbox = QtWidgets.QLineEdit(" ")
            textbox.setEnabled(False)
            
            self.setCellWidget(i, 0, combobox)
            self.setCellWidget(i, 1, textbox)
            
            if names[i].lower() + "Text" in settings.keys():
                textbox.setText(settings[names[i].lower() + "Text"])
                combobox.setCurrentIndex(settings[names[i].lower() + "Index"])

        self.setTableSize()
        
    def updateTypes(self, index, i):
        item = self.cellWidget(i, 1)

        if index == 0:
            item.setEnabled(False)
            item.setText(" ")
        else:
            item.setEnabled(True)
            if item.text() == " ":
                item.setText("0")
            
            if index == 1:
                v = QtGui.QIntValidator(0, 9999, self)
                item.setValidator(v)
                item.setText(item.text().split(".")[0])

            else:
                v = QtGui.QDoubleValidator(self)
                item.setValidator(v)
                item.setText(str(float(item.text())))


    def setTableSize(self):
        w = self.verticalHeader().width() + 30
        for i in range(self.columnCount()):
            w += self.columnWidth(i)
        h = self.horizontalHeader().height() + 4
        for i in range(self.rowCount()):    
            h += self.rowHeight(i)
        self.setMinimumSize(QtCore.QSize(w, h))
        self.setMaximumHeight(h)
        

class FitICASettings(CustomSettings):
        
    def __init__(self, parent, settings):
        super(FitICASettings, self).__init__(parent, settings)

    # Build the settings UI
    def buildUI(self, settings):
    
        self.baseLayout = QtWidgets.QVBoxLayout()
        self.layout = QtWidgets.QFormLayout()
        
        # ICA method
        label = QtWidgets.QLabel("ICA Method")
        self.methodWidget = QtWidgets.QComboBox()
        self.methodWidget.addItems(["fastica", "infomax", "extended-infomax", "picard"])
        if "method" in settings.keys():
            self.methodWidget.setCurrentText(settings["method"])
        self.layout.insertRow(-1, label, self.methodWidget)
        
        # Random state
        label = QtWidgets.QLabel("Fixed Random State")
        self.randomStateWidget = QtWidgets.QCheckBox()
        if "randomState" in settings.keys():
            self.randomStateWidget.setChecked(settings["randomState"])
        self.layout.insertRow(-1, label, self.randomStateWidget)
        
        # Start
        self.startWidget = LinkedSpinbox()
        self.startLabel = LinkedCheckbox("Start", self.startWidget)
        self.startLabel.buildLinkedCheckbox("start", self.settings)
        self.layout.insertRow(-1, self.startLabel, self.startWidget)
        
        # Stop
        self.stopWidget = LinkedSpinbox()
        self.stopLabel = LinkedCheckbox("Stop", self.stopWidget)
        self.stopLabel.buildLinkedCheckbox("stop", self.settings)
        self.layout.insertRow(-1, self.stopLabel, self.stopWidget)
        
        # Link start and stop
        self.startWidget.linkWidgets(self.stopWidget, "Higher")
        self.stopWidget.linkWidgets(self.startWidget, "Lower")
        
        self.criterionWidget = CriterionTable(settings)
        
        self.layout.setSpacing(5)
        
        self.baseLayout.addItem(self.layout)
        self.baseLayout.addWidget(self.criterionWidget)
        self.setLayout(self.baseLayout)
        return
        
    def updateGlobals(self, globals):
        self.stopWidget.setMaximum(int(globals["Data Length"]["value"]))
        return   
        
    # Return the values from each setting type
    def genSettings(self):
        
        varList = {}
        settingList = {}
        
        settingList["settingsFile"] = self.settings["settingsFile"]
        settingList["settingsClass"] = self.settings["settingsClass"]
        
        varList["method"] = self.methodWidget.currentText()
        settingList["method"] = varList["method"]
        
        varList["randomState"] = self.randomStateWidget.isChecked()
        settingList["randomState"] = varList["randomState"]
        
        self.startLabel.getSettings("start", varList, settingList)
        self.stopLabel.getSettings("stop", varList, settingList)

        nameList = ["skew", "kurt", "var"]
        for i in range(3):
            index = self.criterionWidget.cellWidget(i, 0).currentIndex()
            text = self.criterionWidget.cellWidget(i, 1).text()
            if index == 0:
                varList[nameList[i]] = None
            elif index == 1:
                varList[nameList[i]] = int(text)
            else:
                varList[nameList[i]] = float(text)
            
            settingList[nameList[i] + "Index"] = index
            settingList[nameList[i] + "Text"] = text
    
        self.parent.variables = varList
        self.parent.settings = settingList


class fitICA(Node):

    def __init__(self, name, params):
        super(fitICA, self).__init__(name, params)
        
        if self.parameters["skew"] == "None":
            self.parameters["skew"] = None
            
        if self.parameters["kurt"] == "None":
            self.parameters["kurt"] = None
            
        if self.parameters["var"] == "None":
            self.parameters["var"] = None
        
    def process(self):  
    
        # Possibly will be epoch data - needs to work for both
        data = self.args["Raw/Epoch"] 
        
        randomState = None
        if self.parameters["randomState"] == True:
            randomState = 1
            
        # Look at docs for this function https://mne.tools/dev/generated/mne.preprocessing.run_ica.html
        ica = mne.preprocessing.run_ica(data, 
                                    n_components=None, 
                                    max_pca_components=None,
                                    random_state=randomState, 
                                    start=self.parameters["start"],
                                    stop=self.parameters["stop"],
                                    ecg_ch=None, # Need to replace with autofill data taken from channel list
                                    skew_criterion=self.parameters["skew"], 
                                    kurt_criterion=self.parameters["kurt"], 
                                    var_criterion=self.parameters["var"],
                                    method=self.parameters["method"])

        return {"ICA Solution" : ica}