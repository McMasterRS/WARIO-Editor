from PyQt5 import QtWidgets, QtWebEngineWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

def getIcon(str):
    return QtWidgets.QWidget().style().standardIcon(getattr(QtWidgets.QStyle,str))

class HelpUITreeItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, name, url):
        super(HelpUITreeItem, self).__init__()
        self.setText(0, name)
        self.url = QtCore.QUrl(QtCore.QFileInfo(url).absoluteFilePath())

class HelpUI(QtWidgets.QWidget):
    def __init__(self, parent):
        super(HelpUI, self).__init__()
        
        self.parent = parent
        self.resize(1100, 700)
        
        self.loadedTabs = []
        
        self.layout = QtWidgets.QHBoxLayout()
        
        self.tabs = QtWidgets.QTabWidget()
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        
        self.toolkitList = []
        
        self.buildTab("./site/", "WARIO")
        
    
    def buildTab(self, path, toolkit = None):
        
        tab = QtWidgets.QWidget()
        tabLayout = QtWidgets.QHBoxLayout()
        tab.setLayout(tabLayout)
        
        tabWebView = QtWebEngineWidgets.QWebEngineView()
        tabLayout.addWidget(tabWebView)
        tabWebView.setUrl(QtCore.QUrl(QtCore.QFileInfo(path + "/index.html").absoluteFilePath()))
        self.tabs.addTab(tab, toolkit)
        
    def buildToolkitHelp(self):
        
        existingTabs = {}
        
        for i in range(1, self.tabs.count()):
            existingTabs[self.tabs.tabText(i)] = self.tabs.widget(i)
            
        while self.tabs.count() > 1:
            self.tabs.removeTab(1)
            
        for toolkit in self.parent.toolkits:
            if toolkit in existingTabs.keys():
                self.tabs.addTab(existingTabs[toolkit], toolkit)
            else:
                self.buildTab(self.parent.toolkitUI.toolkitPaths[toolkit] + "/site/", toolkit + " toolkit")           