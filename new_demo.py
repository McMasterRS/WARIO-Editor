from PyQt5 import QtWidgets, QtGui
import nodz_main
import sys, os


    
def startNodz():
    try:
        app = QtWidgets.QApplication([])
    except:
        # I guess we're running somewhere that already has a QApp created
        app = None


    nodz = nodz_main.Nodz(None)
    # nodz.loadConfig(filePath='')  
    nodz.initialize()
    
    def makeToolkitCall(name):
        def toolkitCall(state):
            nodz.reloadConfig(name, state)
        return toolkitCall

    window = QtWidgets.QMainWindow()
    window.setCentralWidget(nodz)
    menu = window.menuBar()
    
    fileMenu = menu.addMenu('&File')
    editMenu = menu.addMenu('&Edit')
    toolkitMenu = menu.addMenu("&Toolkits")

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

    duplicateAct = QtWidgets.QAction(QtGui.QIcon('copy.png'), "&Duplicate", window)
    duplicateAct.setShortcut("Ctrl+C")
    duplicateAct.setStatusTip("Duplicate selected nodes")
    duplicateAct.triggered.connect(nodz._copySelectedNodes)

    clearAct = QtWidgets.QAction(QtGui.QIcon('clear.png'), "&Clear flowchart", window)
    clearAct.setStatusTip("Clear flowchart of all nodes")
    clearAct.triggered.connect(nodz.clearGraph)

    editMenu.addAction(duplicateAct)
    editMenu.addAction(clearAct)

    for root, directories, files in os.walk('./toolkits'):
        for dir in directories:
            if dir != "default":
                dirMenu = QtWidgets.QAction(QtGui.QIcon(''), dir, window, checkable=True)
                dirMenu.triggered.connect(makeToolkitCall(dir))
                toolkitMenu.addAction(dirMenu)
        break

    aboutAct = QtWidgets.QAction(QtGui.QIcon('about.png'), "&About", window)
    repoAct = QtWidgets.QAction(QtGui.QIcon('repo.png'), "&Repository", window)
    wikiAct = QtWidgets.QAction(QtGui.QIcon('wiki.png'), "&Wiki", window)

    helpMenu = menu.addMenu('&Help')
    helpMenu.addAction(aboutAct)
    helpMenu.addAction(repoAct)
    helpMenu.addAction(wikiAct)

    window.show()
    


    ######################################################################
    # Test signals
    ######################################################################
    '''
    # Nodes
    @QtCore.Slot(str)
    def on_nodeCreated(nodeName):
        print('node created : ', nodeName)

    @QtCore.Slot(str)
    def on_nodeDeleted(nodeName):
        print('node deleted : ', nodeName)

    @QtCore.Slot(str, str)
    def on_nodeEdited(nodeName, newName):
        print('node edited : {0}, new name : {1}'.format(nodeName, newName))

    @QtCore.Slot(str)
    def on_nodeSelected(nodesName):
        print('node selected : ', nodesName)

    @QtCore.Slot(str, object)
    def on_nodeMoved(nodeName, nodePos):
        print('node {0} moved to {1}'.format(nodeName, nodePos))

    # Attrs
    @QtCore.Slot(str, int)
    def on_attrCreated(nodeName, attrId):
        print('attr created : {0} at index : {1}'.format(nodeName, attrId))

    @QtCore.Slot(str, int)
    def on_attrDeleted(nodeName, attrId):
        print('attr Deleted : {0} at old index : {1}'.format(nodeName, attrId))

    @QtCore.Slot(str, int, int)
    def on_attrEdited(nodeName, oldId, newId):
        print('attr Edited : {0} at old index : {1}, new index : {2}'.format(nodeName, oldId, newId))

    # Connections
    @QtCore.Slot(str, str, str, str)
    def on_connected(srcNodeName, srcPlugName, destNodeName, dstSocketName):
        print('connected src: "{0}" at "{1}" to dst: "{2}" at "{3}"'.format(srcNodeName, srcPlugName, destNodeName, dstSocketName))

    @QtCore.Slot(str, str, str, str)
    def on_disconnected(srcNodeName, srcPlugName, destNodeName, dstSocketName):
        print('disconnected src: "{0}" at "{1}" from dst: "{2}" at "{3}"'.format(srcNodeName, srcPlugName, destNodeName, dstSocketName))

    # Graph
    @QtCore.Slot()
    def on_graphSaved():
        print('graph saved !')

    @QtCore.Slot()
    def on_graphLoaded():
        print('graph loaded !')

    @QtCore.Slot()
    def on_graphCleared():
        print('graph cleared !')

    @QtCore.Slot()
    def on_graphEvaluated():
        print('graph evaluated !')

    # Other
    @QtCore.Slot(object)
    def on_keyPressed(key):
        print('key pressed : ', key)

    nodz.signal_NodeCreated.connect(on_nodeCreated)
    nodz.signal_NodeDeleted.connect(on_nodeDeleted)
    nodz.signal_NodeEdited.connect(on_nodeEdited)
    nodz.signal_NodeSelected.connect(on_nodeSelected)
    nodz.signal_NodeMoved.connect(on_nodeMoved)

    nodz.signal_AttrCreated.connect(on_attrCreated)
    nodz.signal_AttrDeleted.connect(on_attrDeleted)
    nodz.signal_AttrEdited.connect(on_attrEdited)

    nodz.signal_PlugConnected.connect(on_connected)
    nodz.signal_SocketConnected.connect(on_connected)
    nodz.signal_PlugDisconnected.connect(on_disconnected)
    nodz.signal_SocketDisconnected.connect(on_disconnected)

    nodz.signal_GraphSaved.connect(on_graphSaved)
    nodz.signal_GraphLoaded.connect(on_graphLoaded)
    nodz.signal_GraphCleared.connect(on_graphCleared)
    nodz.signal_GraphEvaluated.connect(on_graphEvaluated)

    nodz.signal_KeyPressed.connect(on_keyPressed)
    '''

    if app:
        # command line stand alone test... run our own event loop
        app.exec_()
    
if __name__ == "__main__":
    startNodz()
