from extensions.customSettings import CustomSettings
import importlib
import inspect

from PyQt5 import QtWidgets
from PyQt5 import QtCore

class CustomNodeSettings(CustomSettings):
    def __init__(self, parent, settings):
        self.customFilePath = ""
        self.customSettingsClass = ""
        
        self.customWidget = None
        
        super(CustomNodeSettings, self).__init__(parent, settings)
        
    def buildUI(self, settings):
        
        self.layout = QtWidgets.QHBoxLayout()

        self.loadButton = QtWidgets.QPushButton("Browse")
        self.loadButton.clicked.connect(self.loadCustom)
        self.layout.addWidget(self.loadButton)
        self.resize(200, 50)
        
        self.setLayout(self.layout)
        
    def loadCustom(self):
        f = QtWidgets.QFileDialog.getOpenFileName(filter = "Python Files (*.py)")[0]
        if f is not "":
            spec = importlib.util.spec_from_file_location(name = "Custom", location = f)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            classList = [m[0] for m in inspect.getmembers(module, inspect.isclass) if m[1].__module__ == 'Custom']
                
            settingsCls, ok = QtWidgets.QInputDialog.getItem(self, "Select Settings Class", "Settings Class:", classList, 0, False)
            if ok is False:
                return
                
            self.customFilePath = f
            self.customSettingsClass = settingsCls
            
            settings = {"settingsFile" : self.customFilePath,
                        "settingsClass" : self.customSettingsClass}
            
            self.customWidget = getattr(module, settingsCls)(self.parent, settings)
            
            name, ok = QtWidgets.QInputDialog.getText(self, "Select Name", "Node Name:")
            
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.layout.setSpacing(0)
            self.loadButton.setVisible(False)
            self.layout.replaceWidget(self.loadButton, self.customWidget)
            self.parent.name = name
            
            attribs = self.customWidget.getAttribs()
            
            for attrib in attribs:
                index = attribs[attrib]['index']
                name = attrib
                plug = attribs[attrib]['plug']
                socket = attribs[attrib]['socket']
                preset = attribs[attrib]['preset']
                dataType = attribs[attrib]['type']
                self.parent._createAttribute(name=name,
                                             index=index,
                                             preset=preset,
                                             plug=plug,
                                             socket=socket,
                                             dataType=dataType)
            
    def genSettings(self):
    
        settings = {}
        vars = {}
    
        if self.customWidget is None:
            settings["settingsFile"] = self.settings["settingsFile"]
            settings["settingsClass"] = self.settings["settingsClass"]
            
            self.parent.settings = settings
            self.parent.variables = vars
        else:
            self.customWidget.genSettings()