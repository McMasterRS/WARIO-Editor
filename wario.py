from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5 import QtWidgets, QtGui, QtCore
import nodz.nodz_main as nodz_main
from pipeline.RunPipeline import runPipeline
from extensions.genGraph import generateGraph
import sys, os, textwrap

version = "0.0.1"

def getIcon(str):
    return QtWidgets.QWidget().style().standardIcon(getattr(QtWidgets.QStyle,str))

class NodzWindow(QtWidgets.QMainWindow):
    def __init__(self, nodz):
        QtWidgets.QMainWindow.__init__(self)
        self.nodz = nodz
        self.nodz.parent = self
        #self.threadpool = QtCore.QThreadPool()
        #self.runningPipeline = False
        
        self.installEventFilter(self)
        
        self.setupWindow()
        self.loadToolkitSettings()  
        
    def loadToolkitSettings(self):
    
        file = "./toolkits/toolkitConfig.json"
        if os.path.exists(file):
            self.nodz.toolkitUI.loadToolkitSettings()
        else:
            self.nodz.toolkitUI.genSettings()
        
    def setupWindow(self):
        self.setWindowTitle("WARIO")
        self.setCentralWidget(self.nodz)
        self.setWindowIcon(getIcon("SP_TitleBarMenuButton"))
        self.setStyleSheet("""QMenuBar {
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
            
        self.menu = self.menuBar()
        self.fileMenu = self.menu.addMenu('&File')
        self.editMenu = self.menu.addMenu('&Edit')
        self.toolkitMenu = self.menu.addMenu("&Toolkits")
        self.helpMenu = self.menu.addMenu('&Help')
        
        self.buildFileMenu()
        self.buildEditMenu()
        self.buildToolkitMenu()
        self.buildHelpMenu()
        
    def clearGraph(self):
        self.nodz.clearGraph()
        self.nodz.currentFileName = ""
        
    def saveFile(self):
        self.nodz.saveGraphDialog()
        if self.nodz.currentFileName != "":
            self.setWindowTitle("WARIO - " + self.nodz.currentFileName)
            
    def loadFile(self):
        self.nodz.loadGraphDialog()
        if self.nodz.currentFileName != "":
            # Auto check toolkit options based on what the loaded file uses
            toolkitList = self.nodz.toolkits
            for tk in self.toolkitMenu.actions():
                if tk.text() in toolkitList:
                    tk.setChecked(True)
                else:
                    tk.setChecked(False)
                    
                self.setWindowTitle("WARIO - " + self.nodz.currentFileName)
                
    def saveRunFile(self):
        #if not self.runningPipeline:
            #self.runningPipeline = True
        if self.nodz.currentFileName != "":
            self.nodz.saveGraph(self.nodz.currentFileName)
            runPipeline(self.nodz.currentFileName)
        else:
            self.loadFile()
            if self.nodz.currentFileName != "":
                runPipeline(self.nodz.currentFileName)
        
    def plotGraph(self):
        if self.nodz.currentFileName == "":
            self.loadFile()
            
        if self.nodz.currentFileName != "":
            dialog = QtWidgets.QFileDialog.getSaveFileName(caption = "Graph Save Location",directory='.', filter="PDF files (*.pdf)")
            if (dialog[0] != ''):
                generateGraph(self.nodz.currentFileName, dialog[0])
                    
    def buildFileMenu(self):
 
        # Clear
        clearAct = QtWidgets.QAction(getIcon('SP_FileIcon'), "&New", self)
        clearAct.setShortcut("Ctrl+N")
        clearAct.setStatusTip("Clear flowchart of all nodes")
        clearAct.triggered.connect(self.clearGraph)
        
        # Save
        saveAct = QtWidgets.QAction(getIcon('SP_DialogSaveButton'), "&Save", self)
        saveAct.setShortcut("Ctrl+S")
        saveAct.setStatusTip("Save Flowchart")
        saveAct.triggered.connect(self.saveFile)
        
        # Run
        saveRunAct = QtWidgets.QAction(getIcon('SP_DriveHDIcon'), "Run", self)
        saveRunAct.setShortcut("Ctrl+R")
        saveRunAct.setStatusTip("Save flowchart and run")
        saveRunAct.triggered.connect(self.saveRunFile)
    
        # Load
        loadAct = QtWidgets.QAction(getIcon('SP_DialogOpenButton'), "&Load", self)
        loadAct.setShortcut("Ctrl+L")
        loadAct.setStatusTip("Load Flowchart")
        loadAct.triggered.connect(self.loadFile)
        
        # Graph
        graphAct = QtWidgets.QAction(getIcon('SP_FileDialogListView'), "&Plot Graph", self)
        graphAct.setStatusTip("Plot Graph")
        graphAct.triggered.connect(self.plotGraph)
        
        # Quit
        quitAct = QtWidgets.QAction(getIcon('SP_DialogCancelButton'), "&Quit", self)
        quitAct.setStatusTip("Quit")
        quitAct.triggered.connect(self.nodz.checkClose)
        
        # Link to menu
        self.fileMenu.addAction(clearAct)
        self.fileMenu.addAction(saveAct)  
        self.fileMenu.addAction(loadAct)
        self.fileMenu.addAction(saveRunAct)
        self.fileMenu.addAction(graphAct)    
        self.fileMenu.addAction(quitAct)
    
    def buildEditMenu(self):
    
        globalAct = QtWidgets.QAction(getIcon('SP_ComputerIcon'), "&Global Settings", self)
        globalAct.setShortcut("Ctrl+G")
        globalAct.setStatusTip("Open global settings window")   
        globalAct.triggered.connect(self.nodz.openGlobals)

        self.editMenu.addAction(globalAct)
        
    def makeToolkitCall(self, name):
        # Function generator that creates individual function calls for each of the 
        # toolboxes to handle them being enabled/disabled
        nodz = self.nodz
        toolkitMenu = self.toolkitMenu
        
        def toolkitCall(state):
            ret = nodz.reloadConfig(name, state)
            nodz.helpUI.buildToolkitHelp(nodz.toolkits)
            if ret == False:
                for tk in toolkitMenu.actions():
                    if tk.text() == name:
                        tk.setChecked(True)
                        
        return toolkitCall    
        
    def buildToolkitToggles(self):
        self.toolkitMenu.clear()
        
        for tk in self.nodz.toolkitUI.toolkitNames:
            dirMenu = QtWidgets.QAction(QtGui.QIcon(''), tk, self, checkable=True)
            dirMenu.triggered.connect(self.makeToolkitCall(tk))
            self.toolkitMenu.addAction(dirMenu)
            
        # Check the toolkits that are currently loaded in nodz
        toolkitList = self.nodz.toolkits
        for tk in self.toolkitMenu.actions():
            if tk.text() in toolkitList:
                tk.setChecked(True)
            else:
                tk.setChecked(False)
                
        self.toolkitMenu.addAction(self.toolkitAct)
    
    def buildToolkitMenu(self):
    
        self.toolkitAct = QtWidgets.QAction(QtGui.QIcon(''), "Configure", self)
        self.toolkitAct.triggered.connect(self.nodz.openToolkit)
        self.buildToolkitToggles()
     
    def showAbout(self):
        abt = QtWidgets.QMessageBox.about(nodz, "About", 
        textwrap.dedent('''\
            WARIO - Workplace Automation and Research IO
        
            Version {0}
                    
            Data pipeline with integrated flowchart-based interface allowing for the quick and effective development of complex data analysis flows.

            Developed by Ron Harwood, Thomas Mudway and Oliver Cook at the McMaster University Research Software Engineering group 
            '''.format(version)))
    
    def openRepo(self):
        url = QtCore.QUrl("https://gits.mcmaster.ca/harwood/nodz")
        if not QtGui.QDesktopServices.openUrl(url):
            QtGui.QMessageBox.warning(self, 'Open Url', 'Could not open url')
            
    def openHelp(self):
        self.nodz.openHelp()
            
    def buildHelpMenu(self):
        aboutAct = QtWidgets.QAction(getIcon('SP_MessageBoxQuestion'), "&About", self)
        aboutAct.triggered.connect(self.showAbout)   
        repoAct = QtWidgets.QAction(QtGui.QIcon('repo.png'), "&Repository", self)
        repoAct.triggered.connect(self.openRepo)
        wikiAct = QtWidgets.QAction(QtGui.QIcon('wiki.png'), "&Help", self)
        wikiAct.triggered.connect(self.openHelp)
        
        self.helpMenu.addAction(aboutAct)
        self.helpMenu.addAction(repoAct)
        self.helpMenu.addAction(wikiAct)
        
    def eventFilter(self, object, event):
        # Show save prompt on close
        if event.type() == QtCore.QEvent.Close:
            self.nodz.checkClose()
            # If it makes it this far it was cancelled
            # and we need to ignore the event
            event.ignore()
            return True
            
        return False
        
    def pipelineFinished(self):
        self.runningPipeline = False
    
def startNodz():

    app = QtWidgets.QApplication([])

    nodz = nodz_main.Nodz(None)  
    nodz.initialize()   

    window = NodzWindow(nodz)
    window.show()
    
    app.exec_()
    
if __name__ == "__main__":
    startNodz()
