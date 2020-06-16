from PyQt5 import QtWidgets, QtWebEngineWidgets
from PyQt5 import QtCore

import os
# Returns an icon from a QT icon code
def getIcon(str):
    return QtWidgets.QWidget().style().standardIcon(getattr(QtWidgets.QStyle,str))

# Help menu UI class
class HelpUI(QtWidgets.QWidget):
    def __init__(self, parent):
        super(HelpUI, self).__init__()
        
        self.parent = parent
        self.resize(1100, 700)
      
        self.layout = QtWidgets.QHBoxLayout()
        
        # Each toolkit has its own tab
        self.tabs = QtWidgets.QTabWidget()
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
       
        # Build a tab for the default WARIO documentation held in the "docs" folder
        self.buildTab(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "docs","_build"), "WARIO")        
    
    # Build a tab based on a given toolkit URL and name
    def buildTab(self, path, name):
        
        tab = QtWidgets.QWidget()
        tabLayout = QtWidgets.QHBoxLayout()
        tab.setLayout(tabLayout)
        
        # Create webpage
        tabWebView = QtWebEngineWidgets.QWebEngineView()
        tabLayout.addWidget(tabWebView)
        # Set URL to be index of the toolkit's documentation
        tabWebView.setUrl(QtCore.QUrl.fromLocalFile(os.path.join(path, "index.html")))
        self.tabs.addTab(tab, name)
        
    # Build tabs based on loaded toolkits
    # While the deletion and rebuilding seems redundant, it has a minimal cost and helps
    # make sure that the order of the tabs matches the order of the toolkit drop down menu
    def buildToolkitHelp(self):
        
        existingTabs = {}
        
        # Create list of existing tabs
        for i in range(1, self.tabs.count()):
            existingTabs[self.tabs.tabText(i)] = self.tabs.widget(i)
            
        # Remove all the tabs
        while self.tabs.count() > 1:
            self.tabs.removeTab(1)
            
        # Rebuild the tabs based on what toolkits are loaded
        for toolkit in self.parent.toolkits:
            if toolkit in existingTabs.keys():
                self.tabs.addTab(existingTabs[toolkit], toolkit)
            else:
                self.buildTab(self.parent.toolkitUI.toolkitDocs[toolkit], toolkit + " toolkit")           