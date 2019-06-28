from PyQt5 import QtWidgets, QtGui
import nodz_main
import sys, os

def startNodz():

    app = QtWidgets.QApplication([])

    nodz = nodz_main.Nodz(None)  
    nodz.initialize()

    window = QtWidgets.QMainWindow()
    window.setWindowTitle("WARIO")
    window.setCentralWidget(nodz)
    window.setStyleSheet("""QMenuBar {
            background-color: rgb(49,49,49);
            color: rgb(255,255,255);
            border: 1px solid #000;
        }

        QMenuBar::item {
            background-color: rgb(49,49,49);
            color: rgb(255,255,255);
        }

        QMenuBar::item::selected {
            background-color: rgb(30,30,30);
        }

        QMenu {
            background-color: rgb(49,49,49);
            color: rgb(255,255,255);
            border: 1px solid #000;           
        }

        QMenu::item::selected {
            background-color: rgb(30,30,30);
        }""")
        
    menu = window.menuBar()
    fileMenu = menu.addMenu('&File')
    editMenu = menu.addMenu('&Edit')
    toolkitMenu = menu.addMenu("&Toolkits")

    ### FILE MENU

    saveAct = QtWidgets.QAction(QtGui.QIcon('save.png'), "&Save", window)
    saveAct.setShortcut("Ctrl+S")
    saveAct.setStatusTip("Save Flowchart")
    saveAct.triggered.connect(nodz.saveGraphDialog)
    
    def loadFile():
        nodz.loadGraphDialog()
        toolkitList = nodz.toolkits
        for tk in toolkitMenu.actions():
            if tk.text() in toolkitList:
                tk.setChecked(True)
            else:
                tk.setChecked(False)

    loadAct = QtWidgets.QAction(QtGui.QIcon('load.png'), "&Load", window)
    loadAct.setShortcut("Ctrl+O")
    loadAct.setStatusTip("Load Flowchart")
    loadAct.triggered.connect(loadFile)

    quitAct = QtWidgets.QAction(QtGui.QIcon('quit.png'), "&Quit", window)
    quitAct.setStatusTip("Quit")
    quitAct.triggered.connect(nodz.checkClose)

    fileMenu.addAction(saveAct)  
    fileMenu.addAction(loadAct)
    fileMenu.addAction(quitAct)
    
    ### EDIT MENU
    
    duplicateAct = QtWidgets.QAction(QtGui.QIcon('copy.png'), "&Duplicate", window)
    duplicateAct.setShortcut("Ctrl+C")
    duplicateAct.setStatusTip("Duplicate selected nodes")
    duplicateAct.triggered.connect(nodz._copySelectedNodes)

    clearAct = QtWidgets.QAction(QtGui.QIcon('clear.png'), "&Clear flowchart", window)
    clearAct.setStatusTip("Clear flowchart of all nodes")
    clearAct.triggered.connect(nodz.clearGraph)

    editMenu.addAction(duplicateAct)
    editMenu.addAction(clearAct)

    def makeToolkitCall(name):
        def toolkitCall(state):
            nodz.reloadConfig(name, state)
        return toolkitCall

    for root, directories, files in os.walk('./toolkits'):
        for dir in directories:
            if dir != "default":
                dirMenu = QtWidgets.QAction(QtGui.QIcon(''), dir, window, checkable=True)
                dirMenu.triggered.connect(makeToolkitCall(dir))
                toolkitMenu.addAction(dirMenu)
        break
    reloadAct = QtWidgets.QAction(QtGui.QIcon(''), "Reload", window)
    reloadAct.triggered.connect(nodz.reloadConfig)
    toolkitMenu.addAction(reloadAct)

    ### ABOUT MENU
    
    aboutAct = QtWidgets.QAction(QtGui.QIcon('about.png'), "&About", window)
    repoAct = QtWidgets.QAction(QtGui.QIcon('repo.png'), "&Repository", window)
    wikiAct = QtWidgets.QAction(QtGui.QIcon('wiki.png'), "&Wiki", window)

    helpMenu = menu.addMenu('&Help')
    helpMenu.addAction(aboutAct)
    helpMenu.addAction(repoAct)
    helpMenu.addAction(wikiAct)

    window.show()
    
    app.exec_()
    
if __name__ == "__main__":
    startNodz()
