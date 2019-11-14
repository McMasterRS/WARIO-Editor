from PyQt5 import QtWidgets, QtWebEngineWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

import os

def getIcon(str):
    return QtWidgets.QWidget().style().standardIcon(getattr(QtWidgets.QStyle,str))

class HelpUITreeItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, name):
        super(HelpUITreeItem, self).__init__()
        self.setText(0, name)
        self.url = ""
        #self.setIcon(0, getIcon("SP_DirIcon"))


class HelpUI(QtWidgets.QWidget):
    def __init__(self):
        super(HelpUI, self).__init__()
        self.layout = QtWidgets.QHBoxLayout()
        
        self.treeMenu = QtWidgets.QTreeWidget()
        self.layout.addWidget(self.treeMenu)
        
        self.webView = QtWebEngineWidgets.QWebEngineView()
        self.webView.setUrl(QtCore.QUrl("file:///C:/Users/mudwayt/Documents/GitHub/nodz/nodz/help/home.html"))
        self.layout.addWidget(self.webView)
        
        self.setLayout(self.layout)
        
        self.buildTree()
        
    def buildTree(self):
        self.treeMenu.setColumnCount(1)
        self.treeMenu.setHeaderHidden(True)
        homeItem = HelpUITreeItem("Home")
        homeItem.addChild(HelpUITreeItem("Test"))
        self.treeMenu.addTopLevelItem(homeItem) 