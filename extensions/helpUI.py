from PyQt5 import QtWidgets, QtWebEngineWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

import os

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
        
        self.layout = QtWidgets.QHBoxLayout()
        
        self.treeMenu = QtWidgets.QTreeWidget()
        self.treeMenu.currentItemChanged.connect(self.updateURL)
        self.treeMenu.setHeaderHidden(True)
        self.layout.addWidget(self.treeMenu)
        
        self.webView = QtWebEngineWidgets.QWebEngineView()
        self.layout.addWidget(self.webView)
        
        self.setLayout(self.layout)
        
        self.toolkitList = []
        
        self.buildTree(os.path.normpath("./help/"))
        
    def buildTree(self, path, toolkit = None):
        self.treeMenu.blockSignals(True)        
        
        if toolkit is None:
            treeDepth = -1
            treeDirectories = []
        else:
            treeDepth = 0
            base = HelpUITreeItem(toolkit + " Toolkit", os.path.normpath(path + "/default.html"))
            self.treeMenu.addTopLevelItem(base)
            treeDirectories = [base]
            self.toolkitList.append(base)
        
        for dirpath, dnames, fnames in os.walk(path):
        
            for fname in fnames: 
                if fname == "default.html":
                    continue
                item = HelpUITreeItem(fname.split(".")[0], os.path.normpath(dirpath + "/" + fname))
                
                if treeDepth == -1:
                    self.treeMenu.addTopLevelItem(item)
                else:
                    treeDirectories[treeDepth].addChild(item)  
                        
            for dname in dnames:
                if dname[0] == "_":
                    continue
                item = HelpUITreeItem(dname.split("/")[-1], os.path.normpath(dirpath + "/" + dname + "/default.html"))
                treeDirectories.append(item)
                
                if treeDepth == -1:
                    self.treeMenu.addTopLevelItem(item)
                else:
                    treeDirectories[treeDepth].addChild(item)  
                    
            treeDepth += 1        
            
        self.treeMenu.blockSignals(False)
        
    def buildToolkitHelp(self, toolkits):
        # Refresh the toolkits
        for toolkit in self.toolkitList:
            self.treeMenu.invisibleRootItem().removeChild(toolkit)
            
        for toolkit in toolkits:
            self.buildTree(os.path.normpath(self.parent.toolkitUI.toolkitPaths[toolkit] + "/help/"), toolkit)

        
    def updateURL(self, current, prev):
        self.webView.setUrl(current.url)