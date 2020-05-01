from PyQt5 import QtWidgets, QtGui, QtCore
import nodz.nodz_main as nodz_main
from RunPipeline import ThreadHandler
from extensions.GenGraph import generateGraph
from extensions.WarioSettings import WarioSettings
import sys, os, textwrap, importlib
from blinker import signal

import subprocess

version = "0.1.0"

# Returns an icon from a given Qt icon code
def getIcon(str):
    return QtWidgets.QWidget().style().standardIcon(getattr(QtWidgets.QStyle,str))
    
# Primary WARIO window
class WarioWindow(QtWidgets.QMainWindow):
    def __init__(self, nodz):
        QtWidgets.QMainWindow.__init__(self)
        # Initialize the Nodz based UI
        self.nodz = nodz
        self.nodz.parent = self

        # Runtime window to be used when running pipelines
        self.handler = None
        
        # WARIO specific settings window
        self.settings = WarioSettings()
        
        self.installEventFilter(self)
        
        self.setupWindow()
        self.setupSignals()
        self.loadToolkitSettings()  
        
    # Loads the existing toolkits into the interface
    def loadToolkitSettings(self):
        
        # Config file path
        file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "toolkits", "toolkitConfig.json")
        
        # If it doesnt exist, create one with whatever toolkits are in the toolkit folder
        if os.path.exists(file):
            self.nodz.toolkitUI.loadToolkitSettings()
        else:
            self.nodz.toolkitUI.genSettings()
        
    # Connects signals for highlighting nodes during runtime
    def setupSignals(self):
        signal('start').connect(self.nodz.initializeNodeEvent)
        signal('node start').connect(self.nodz.activateNodeEvent)
        signal('node complete').connect(self.nodz.completeNodeEvent)
        
    # Set up the interface
    def setupWindow(self):
        # Set the top bar/menu bar settings
        self.setWindowTitle("WARIO Editor")
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
            
        # Build the menu bar
        self.menu = self.menuBar()
        self.fileMenu = self.menu.addMenu('&File')
        self.editMenu = self.menu.addMenu('&Edit')
        self.toolkitMenu = self.menu.addMenu("&Toolkits")
        self.helpMenu = self.menu.addMenu('&Help')
        
        # Populate the menu bar
        self.buildFileMenu()
        self.buildEditMenu()
        self.buildToolkitMenu()
        self.buildHelpMenu()
        
    # Delete all existing nodes in the pipeline
    def clearGraph(self):
        self.nodz.clearGraph()
        self.nodz.currentFileName = ""
        self.setWindowTitle("WARIO Editor")
       
   # Save the pipeline
    def saveFile(self):
        # if a filename has already been set, dont show prompt
        if self.nodz.currentFileName != "":
            self.nodz.saveGraph(self.nodz.currentFileName)
        else:
            self.saveAsFile()
        
    # Save As
    def saveAsFile(self):
        self.nodz.saveGraphDialog()
        if self.nodz.currentFileName != "":
            self.setWindowTitle("WARIO Editor - " + self.nodz.currentFileName)
            
    # Load
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
                    
                self.setWindowTitle("WARIO Editor - " + self.nodz.currentFileName)
                
    # Save the file and run as a pipeline
    def saveRunFile(self):
        
        # Check if the pipeline is already running
        if self.handler is not None:
            if self.handler.running == True:
                return
    
        # If the pipeline hasnt been saved, prompt the save window
        # If there are no nodes, prompt the load window
        if self.nodz.currentFileName != "" and not self.settings.cbSavePrompt.isChecked():
            self.nodz.saveGraph(self.nodz.currentFileName)
        else:
            if len(self.nodz.scene().nodes) != 0:
                self.saveAsFile()
            else:
                self.loadFile()
                
        # Double check that a file was selected/saved (stops run if cancel is hit)
        if self.nodz.currentFileName != "":
            # Run the default thread handler
            if self.settings.rbDefault.isChecked():
                self.handler = ThreadHandler()
                self.handler.show()
                self.handler.startPipeline(self.nodz.currentFileName)
            # Import and run the custom thread handler defined in the settings window
            else:
                spec = importlib.util.spec_from_file_location("handler", self.settings.tbDisplay.text())
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                cls = getattr(mod, "getHandler")
                self.handler = cls(self.nodz.currentFileName)

    # Plots a directed graph of the pipeline
    def plotGraph(self):
        # If no file is loaded, prompt to load
        # FIXME - check if nodes in the window and prompt to save if so
        if self.nodz.currentFileName == "":
            self.loadFile()
            
        # If a file is selected, run code in extensions/genGraph to create plot
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
        
        # Save As
        saveAsAct = QtWidgets.QAction(getIcon('SP_DialogSaveButton'), "Save &As", self)
        saveAsAct.setStatusTip("Save Flowchart as new file")
        saveAsAct.triggered.connect(self.saveAsFile)
        
        # Run
        saveRunAct = QtWidgets.QAction(getIcon('SP_DriveHDIcon'), "&Run", self)
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
        self.fileMenu.addAction(saveAsAct)
        self.fileMenu.addAction(loadAct)
        self.fileMenu.addAction(saveRunAct)
        self.fileMenu.addAction(graphAct)    
        self.fileMenu.addAction(quitAct)
    
    def buildEditMenu(self):
    
        # Show global variables window
        globalAct = QtWidgets.QAction(getIcon('SP_ComputerIcon'), "&Global Variables", self)
        globalAct.setShortcut("Ctrl+G")
        globalAct.setStatusTip("Open global variables window")   
        globalAct.triggered.connect(self.nodz.openGlobals)
        
        # Show WARIO settings window
        settingsAct = QtWidgets.QAction(getIcon('SP_FileDialogDetailedView'), "WARIO &Preferences", self)
        settingsAct.setShortcut("Ctrl+P")
        settingsAct.setStatusTip("Open WARIO Preferences Window")
        settingsAct.triggered.connect(self.openSettings)

        self.editMenu.addAction(settingsAct)
        self.editMenu.addAction(globalAct)
        
    def openSettings(self):
        self.settings.show()
        
        
    # Function generator that creates individual function calls for each of the 
    # toolboxes to handle them being enabled/disabled      
    def makeToolkitCall(self, name):
        nodz = self.nodz
        toolkitMenu = self.toolkitMenu
        
        def toolkitCall(state):
            ret = nodz.reloadConfig(name, state)
            nodz.helpUI.buildToolkitHelp()
            if ret == False:
                for tk in toolkitMenu.actions():
                    if tk.text() == name:
                        tk.setChecked(True)
                        
        return toolkitCall    
        
    # Builds the toolkit actions and connects their generated functions
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

    # Calls the above function and adds the action for the toolkit manager
    def buildToolkitMenu(self):
    
        self.toolkitAct = QtWidgets.QAction(getIcon('SP_DirIcon'), "Manage", self)
        self.toolkitAct.triggered.connect(self.nodz.openToolkit)
        self.buildToolkitToggles()
        
     
    def showAbout(self):
        abt = QtWidgets.QMessageBox.about(self.nodz, "About", 
        textwrap.dedent('''\
            WARIO - Workplace Automation and Research IO
        
            Version {0}
                    
            Data pipeline with integrated flowchart-based interface allowing for the quick and effective development of complex data analysis flows.

            Developed by Ron Harwood, Thomas Mudway and Oliver Cook at the McMaster University Research Software Engineering group 
            '''.format(version)))
    
    # Opens a link to the WARIO editor repoAct
    def openRepo(self):
        url = QtCore.QUrl("https://github.com/McMasterRS/WARIO-Editor")
        if not QtGui.QDesktopServices.openUrl(url):
            QtGui.QMessageBox.warning(self, 'Open Url', 'Could not open url')
            
    # Opens the help menu
    def openHelp(self):
        self.nodz.openHelp()
            
    def buildHelpMenu(self):
        aboutAct = QtWidgets.QAction(getIcon('SP_TitleBarMenuButton'), "&About", self)
        aboutAct.triggered.connect(self.showAbout)   
        repoAct = QtWidgets.QAction(getIcon('SP_MessageBoxInformation'), "&Repository", self)
        repoAct.triggered.connect(self.openRepo)
        wikiAct = QtWidgets.QAction(getIcon('SP_MessageBoxQuestion'), "&Help", self)
        wikiAct.triggered.connect(self.openHelp)
        
        self.helpMenu.addAction(aboutAct)
        self.helpMenu.addAction(repoAct)
        self.helpMenu.addAction(wikiAct)
        
    # Custom event filter
    def eventFilter(self, object, event):
        # Show save prompt on close
        if event.type() == QtCore.QEvent.Close:
            self.nodz.checkClose()
            # If it makes it this far it was cancelled
            # and we need to ignore the event
            event.ignore()
            return True
            
        return False
        
    
def startWario():

    app = QtWidgets.QApplication([])

    nodz = nodz_main.Nodz(None)  
    nodz.initialize()   

    window = WarioWindow(nodz)
    window.show()
    
    app.exec_()
    
if __name__ == "__main__":
    startWario()
