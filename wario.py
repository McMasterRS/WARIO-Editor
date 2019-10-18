from PyQt5 import QtWidgets, QtGui, QtCore
import nodz.nodz_main as nodz_main
from pipeline.RunPipeline import runPipeline
from nodz.genGraph import generateGraph
import sys, os, textwrap

version = "0.0.1"

class NodzWindow(QtWidgets.QMainWindow):
    def __init__(self, nodz):
        QtWidgets.QMainWindow.__init__(self)
        self.nodz = nodz
        self.installEventFilter(self)
    
    def eventFilter(self, object, event):
        # Show save prompt on close
        if event.type() == QtCore.QEvent.Close:
            self.nodz.checkClose()
            # If it makes it this far it was cancelled
            # and we need to ignore the event
            event.ignore()
            return True
            
        return False

def getIcon(str):
    return QtWidgets.QWidget().style().standardIcon(getattr(QtWidgets.QStyle,str))

def startNodz():

    app = QtWidgets.QApplication([])

    nodz = nodz_main.Nodz(None)  
    nodz.initialize()   

    window = NodzWindow(nodz)
    
    window.setWindowTitle("WARIO")
    window.setCentralWidget(nodz)
    window.setWindowIcon(getIcon("SP_TitleBarMenuButton"))
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

    def saveFile():
        nodz.saveGraphDialog()
        if nodz.currentFileName != "":
            window.setWindowTitle("WARIO - " + nodz.currentFileName)
        
    saveAct = QtWidgets.QAction(getIcon('SP_DialogSaveButton'), "&Save", window)
    saveAct.setShortcut("Ctrl+S")
    saveAct.setStatusTip("Save Flowchart")
    saveAct.triggered.connect(saveFile)
    
    def saveRunFile():
        if nodz.currentFileName != "":
            nodz.saveGraph(nodz.currentFileName)
            runPipeline(nodz.currentFileName)
        else:
            nodz.loadGraphDialog()
            if nodz.currentFileName != "":
                window.setWindowTitle("WARIO - " + nodz.currentFileName)
                runPipeline(nodz.currentFileName)
    
    saveRunAct = QtWidgets.QAction(getIcon('SP_DriveHDIcon'), "&Run", window)
    saveRunAct.setShortcut("Ctrl+R")
    saveRunAct.setStatusTip("Save flowchart and run")
    saveRunAct.triggered.connect(saveRunFile)
    
    def loadFile():
        nodz.loadGraphDialog()
        # Auto check toolkit options based on what the loaded file uses
        toolkitList = nodz.toolkits
        for tk in toolkitMenu.actions():
            if tk.text() in toolkitList:
                tk.setChecked(True)
            else:
                tk.setChecked(False)
                
        if nodz.currentFileName != "":
            window.setWindowTitle("WARIO - " + nodz.currentFileName)

    loadAct = QtWidgets.QAction(getIcon('SP_DialogOpenButton'), "&Load", window)
    loadAct.setShortcut("Ctrl+L")
    loadAct.setStatusTip("Load Flowchart")
    loadAct.triggered.connect(loadFile)
    
    def plotGraph():
        if nodz.currentFileName == "":
            nodz.loadGraphDialog()
            if nodz.currentFileName != "":
                window.setWindowTitle("WARIO - " + nodz.currentFileName)
            else:
                return
        
        dialog = QtWidgets.QFileDialog.getSaveFileName(caption = "Graph Save Location",directory='.', filter="PDF files (*.pdf)")
        if (dialog[0] != ''):
            generateGraph(nodz.currentFileName, dialog[0])
    
    graphAct = QtWidgets.QAction(getIcon('SP_FileDialogListView'), "&Plot Graph", window)
    graphAct.setStatusTip("Plot Graph")
    graphAct.triggered.connect(plotGraph)

    quitAct = QtWidgets.QAction(getIcon('SP_DialogCancelButton'), "&Quit", window)
    quitAct.setStatusTip("Quit")
    quitAct.triggered.connect(nodz.checkClose)

    fileMenu.addAction(saveAct)  
    fileMenu.addAction(saveRunAct)
    fileMenu.addAction(loadAct)
    fileMenu.addAction(graphAct)    
    fileMenu.addAction(quitAct)
    
    ### EDIT MENU
    
    globalAct = QtWidgets.QAction(getIcon('SP_ComputerIcon'), "&Global Settings", window)
    globalAct.setShortcut("Ctrl+G")
    globalAct.setStatusTip("Open global settings window")   
    globalAct.triggered.connect(nodz.openGlobals)
    
    duplicateAct = QtWidgets.QAction(getIcon('SP_TitleBarNormalButton'), "&Duplicate Nodes", window)
    duplicateAct.setShortcut("Ctrl+D")
    duplicateAct.setStatusTip("Duplicate selected nodes")
    duplicateAct.triggered.connect(nodz._copySelectedNodes)

    clearAct = QtWidgets.QAction(getIcon('SP_DialogDiscardButton'), "&Clear flowchart", window)
    clearAct.setStatusTip("Clear flowchart of all nodes")
    clearAct.triggered.connect(nodz.clearGraph)

    editMenu.addAction(globalAct)
    #editMenu.addAction(duplicateAct)
    editMenu.addAction(clearAct)

    # Function generator that creates individual function calls for each of the 
    # toolboxes to handle them being enabled/disabled
    def makeToolkitCall(name):
        def toolkitCall(state):
            ret = nodz.reloadConfig(name, state)
            if ret == False:
                for tk in toolkitMenu.actions():
                    if tk.text() == name:
                        tk.setChecked(True)
        return toolkitCall
    
    # Builds the toolkit menu. Needs to be a function so it can be called when
    # reload option is clicked
    def buildToolkitMenu():
    
        toolkitMenu.clear()
        
        for root, directories, files in os.walk('./toolkits'):
            for dir in directories:
                if dir != "default" and dir != "__pycache__":
                    dirMenu = QtWidgets.QAction(QtGui.QIcon(''), dir, window, checkable=True)
                    dirMenu.triggered.connect(makeToolkitCall(dir))
                    toolkitMenu.addAction(dirMenu)
            break
    
        # Check the toolkits that are currently loaded in nodz
        toolkitList = nodz.toolkits
        for tk in toolkitMenu.actions():
            if tk.text() in toolkitList:
                tk.setChecked(True)
            else:
                tk.setChecked(False)
            
    buildToolkitMenu()
    
    ### ABOUT MENU
    
    def showAbout():
        abt = QtWidgets.QMessageBox.about(nodz, "About", 
        textwrap.dedent('''\
            WARIO - Workplace Automation and Research IO
        
            Version {0}
                    
            Data pipeline with integrated flowchart-based interface allowing for the quick and effective development of complex data analysis flows.

            Developed by Ron Harwood, Thomas Mudway and Oliver Cook at the McMaster University Research Software Engineering group 
            '''.format(version)))
    
    def openRepo():
        url = QtCore.QUrl("https://gits.mcmaster.ca/harwood/nodz")
        if not QtGui.QDesktopServices.openUrl(url):
            QtGui.QMessageBox.warning(self, 'Open Url', 'Could not open url')
            
    def openWiki():
        url = QtCore.QUrl("https://gits.mcmaster.ca/harwood/nodz/wikis/home")
        if not QtGui.QDesktopServices.openUrl(url):
            QtGui.QMessageBox.warning(self, 'Open Url', 'Could not open url')
    
    aboutAct = QtWidgets.QAction(getIcon('SP_MessageBoxQuestion'), "&About", window)
    aboutAct.triggered.connect(showAbout)   
    repoAct = QtWidgets.QAction(QtGui.QIcon('repo.png'), "&Repository", window)
    repoAct.triggered.connect(openRepo)
    wikiAct = QtWidgets.QAction(QtGui.QIcon('wiki.png'), "&Wiki", window)
    wikiAct.triggered.connect(openWiki)

    helpMenu = menu.addMenu('&Help')
    helpMenu.addAction(aboutAct)
    helpMenu.addAction(repoAct)
    helpMenu.addAction(wikiAct)

    window.show()
    
    app.exec_()
    
if __name__ == "__main__":
    startNodz()
