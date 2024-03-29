import os
import json
import functools
import sys
import uuid
import importlib

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

import WarioEditor.nodz.nodz_utils as utils

from WarioEditor.extensions.SettingsWindow import SettingsItem
from WarioEditor.extensions.GlobalUI import GlobalUI
from WarioEditor.extensions.HelpUI import HelpUI
from WarioEditor.extensions.ToolkitUI import ToolkitUI

defaultConfigPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')

class Nodz(QtWidgets.QGraphicsView):

    """
    The main view for the node graph representation.

    The node view implements a state pattern to control all the
    different user interactions.

    """

    signal_NodeCreated = QtCore.pyqtSignal(object)
    signal_NodeDeleted = QtCore.pyqtSignal(object)
    signal_NodeEdited = QtCore.pyqtSignal(object, object)
    signal_NodeSelected = QtCore.pyqtSignal(object)
    signal_NodeMoved = QtCore.pyqtSignal(str, object)

    signal_AttrCreated = QtCore.pyqtSignal(object, object)
    signal_AttrDeleted = QtCore.pyqtSignal(object, object)
    signal_AttrEdited = QtCore.pyqtSignal(object, object, object)

    signal_PlugConnected = QtCore.pyqtSignal(object, object, object, object)
    signal_PlugDisconnected = QtCore.pyqtSignal(object, object, object, object)
    signal_SocketConnected = QtCore.pyqtSignal(object, object, object, object)
    signal_SocketDisconnected = QtCore.pyqtSignal(object, object, object, object)

    signal_GraphSaved = QtCore.pyqtSignal()
    signal_GraphLoaded = QtCore.pyqtSignal()
    signal_GraphCleared = QtCore.pyqtSignal()
    signal_GraphEvaluated = QtCore.pyqtSignal()

    signal_KeyPressed = QtCore.pyqtSignal(object)
    signal_Dropped = QtCore.pyqtSignal(object)
    
    def __init__(self, parent, configPath=defaultConfigPath):
        """
        Initialize the graphics view.

        """
        super(Nodz, self).__init__(parent)


        # Global variables
        self.globalUI = GlobalUI(self)
        self.globals = []
        
        # Load nodz configuration.
        self.loadConfig(configPath)
        self.toolkitUI = ToolkitUI(self)
        self.toolkits = []
        
        # Help menu
        self.helpUI = HelpUI(self)
        
        # General data.
        self.gridVisToggle = True
        self.gridSnapToggle = False
        self._nodeSnap = False
        self.selectedNodes = None
        self.currentFileName = ""

        # Connections data.
        self.drawingConnection = False
        self.currentHoveredNode = None
        self.sourceSlot = None

        # Display options.
        self.currentState = 'DEFAULT'
        self.pressedKeys = list()

    def wheelEvent(self, event):
        """
        Zoom in the view with the mouse wheel.

        """
        self.currentState = 'ZOOM_VIEW'
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)

        inFactor = 1.15
        outFactor = 1 / inFactor

        if event.angleDelta().y() > 0:
            zoomFactor = inFactor
        else:
            zoomFactor = outFactor

        self.scale(zoomFactor, zoomFactor)

        self.currentState = 'DEFAULT'

    def mousePressEvent(self, event):
        """
        Initialize tablet zoom, drag canvas and the selection.

        """
        # Tablet zoom
        '''
        if (event.button() == QtCore.Qt.RightButton and
            event.modifiers() == QtCore.Qt.AltModifier):
            self.currentState = 'ZOOM_VIEW'
            self.initMousePos = event.pos()
            self.zoomInitialPos = event.pos()
            self.initMouse = QtGui.QCursor.pos()
            self.setInteractive(False)
        '''
        
        # Creates right click new node menu
        if (event.button() == QtCore.Qt.RightButton ):

            self.currentState = 'MENU'
            menu = QtWidgets.QMenu(self)
            # Category menu - 2D dict that has all categories for all toolkits
            catMenu = dict()
            # Toolkit menu
            tkMenu = dict()

            nodeTypes = self.config['node_types']
            nodeCat = dict()
            nodeTk = dict()
            
            # Loop through nodes currently loaded
            for nt in nodeTypes:
                # Set the toolkit for that node
                nodeTk[nt] = self.config['node_types'][nt]['toolkit']
                
                # Custom added at the end so can skip for now
                if nt == "Custom":
                    continue
                    
                # If toolkit doesnt exist in menu, add it
                if nodeTk[nt] not in tkMenu:
                    if nodeTk[nt] == "":
                        nodeTk[nt] = "Other"
                    tkMenu[nodeTk[nt]] = menu.addMenu(nodeTk[nt])
                    catMenu[nodeTk[nt]] = dict()
                    
                # If category doesnt exist in toolkit, add it
                nodeCat[nt] = self.config['node_types'][nt]['category']
                if nodeCat[nt] not in catMenu[nodeTk[nt]]:
                    if nodeCat[nt] == "":
                        nodeCat[nt] = "Other"
                    catMenu[nodeTk[nt]][nodeCat[nt]] = tkMenu[nodeTk[nt]].addMenu(nodeCat[nt])
                    
                # Trim the name from the key by removing the toolkit appended at the start
                name = nt[len(nodeTk[nt]):]
                
                # Add node to menu
                action = catMenu[nodeTk[nt]][nodeCat[nt]].addAction(name, functools.partial(self.newNode,name=name,attrs=self.config['node_types'][nt],position=self.mapToScene(event.pos()),settings=self.config['node_types'][nt]["settings"], type=nt, toolkit=nodeTk[nt]))
                
            # Add custom node
            menu.addAction('Custom', functools.partial(self.newNode,name='Custom',attrs=self.config['node_types']['Custom'],position=self.mapToScene(event.pos()),settings=self.config['node_types']['Custom']["settings"], type='Custom', toolkit='custom'))

            menu.exec_(event.globalPos())

        # Drag view
        if (event.button() == QtCore.Qt.LeftButton and
              event.modifiers() == QtCore.Qt.AltModifier):
            self.currentState = 'DRAG_VIEW'
            self.prevPos = event.pos()
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            self.setInteractive(False)


        # Rubber band selection
        elif (event.button() == QtCore.Qt.LeftButton and
              event.modifiers() == QtCore.Qt.NoModifier and
              self.scene().itemAt(self.mapToScene(event.pos()), QtGui.QTransform()) is None):
            self.currentState = 'SELECTION'
            self._initRubberband(event.pos())
            self.setInteractive(False)


        # Drag Item
        elif (event.button() == QtCore.Qt.LeftButton and
              event.modifiers() == QtCore.Qt.NoModifier and
              self.scene().itemAt(self.mapToScene(event.pos()), QtGui.QTransform()) is not None):
            self.currentState = 'DRAG_ITEM'
            self.setInteractive(True)


        # Add selection
        elif (event.button() == QtCore.Qt.LeftButton and
              QtCore.Qt.Key_Shift in self.pressedKeys and
              QtCore.Qt.Key_Control in self.pressedKeys):
            self.currentState = 'ADD_SELECTION'
            self._initRubberband(event.pos())
            self.setInteractive(False)


        # Subtract selection
        elif (event.button() == QtCore.Qt.LeftButton and
              event.modifiers() == QtCore.Qt.ControlModifier):
            self.currentState = 'SUBTRACT_SELECTION'
            self._initRubberband(event.pos())
            self.setInteractive(False)


        # Toggle selection
        elif (event.button() == QtCore.Qt.LeftButton and
              event.modifiers() == QtCore.Qt.ShiftModifier):
            self.currentState = 'TOGGLE_SELECTION'
            self._initRubberband(event.pos())
            self.setInteractive(False)


        else:
            self.currentState = 'DEFAULT'

        super(Nodz, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
        Update tablet zoom, canvas dragging and selection.

        """
        # Zoom.
        '''
        if self.currentState == 'ZOOM_VIEW':
            offset = self.zoomInitialPos.x() - event.pos().x()

            if offset > self.previousMouseOffset:
                self.previousMouseOffset = offset
                self.zoomDirection = -1
                self.zoomIncr -= 1

            elif offset == self.previousMouseOffset:
                self.previousMouseOffset = offset
                if self.zoomDirection == -1:
                    self.zoomDirection = -1
                else:
                    self.zoomDirection = 1

            else:
                self.previousMouseOffset = offset
                self.zoomDirection = 1
                self.zoomIncr += 1

            if self.zoomDirection == 1:
                zoomFactor = 1.03
            else:
                zoomFactor = 1 / 1.03

            # Perform zoom and re-center on initial click position.
            pBefore = self.mapToScene(self.initMousePos)
            self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorViewCenter)
            self.scale(zoomFactor, zoomFactor)
            pAfter = self.mapToScene(self.initMousePos)
            diff = pAfter - pBefore

            self.setTransformationAnchor(QtWidgets.QGraphicsView.NoAnchor)
            self.translate(diff.x(), diff.y())
        '''
        # Drag canvas.
        if self.currentState == 'DRAG_VIEW':
            offset = self.prevPos - event.pos()
            self.prevPos = event.pos()
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + offset.y())
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + offset.x())

        # RuberBand selection.
        elif (self.currentState == 'SELECTION' or
              self.currentState == 'ADD_SELECTION' or
              self.currentState == 'SUBTRACT_SELECTION' or
              self.currentState == 'TOGGLE_SELECTION'):
            self.rubberband.setGeometry(QtCore.QRect(self.origin, event.pos()).normalized())

        super(Nodz, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """
        Apply tablet zoom, dragging and selection.

        """
        # Zoom the View.
        if self.currentState == '.ZOOM_VIEW':
            self.offset = 0
            self.zoomDirection = 0
            self.zoomIncr = 0
            self.setInteractive(True)


        # Drag View.
        elif self.currentState == 'DRAG_VIEW':
            self.setCursor(QtCore.Qt.ArrowCursor)
            self.setInteractive(True)


        # Selection.
        elif self.currentState == 'SELECTION':
            self.rubberband.setGeometry(QtCore.QRect(self.origin,
                                                     event.pos()).normalized())
            painterPath = self._releaseRubberband()
            self.setInteractive(True)
            self.scene().setSelectionArea(painterPath)


        # Add Selection.
        elif self.currentState == 'ADD_SELECTION':
            self.rubberband.setGeometry(QtCore.QRect(self.origin,
                                                     event.pos()).normalized())
            painterPath = self._releaseRubberband()
            self.setInteractive(True)
            for item in self.scene().items(painterPath):
                item.setSelected(True)


        # Subtract Selection.
        elif self.currentState == 'SUBTRACT_SELECTION':
            self.rubberband.setGeometry(QtCore.QRect(self.origin,
                                                     event.pos()).normalized())
            painterPath = self._releaseRubberband()
            self.setInteractive(True)
            for item in self.scene().items(painterPath):
                item.setSelected(False)


        # Toggle Selection
        elif self.currentState == 'TOGGLE_SELECTION':
            self.rubberband.setGeometry(QtCore.QRect(self.origin,
                                                     event.pos()).normalized())
            painterPath = self._releaseRubberband()
            self.setInteractive(True)
            for item in self.scene().items(painterPath):
                if item.isSelected():
                    item.setSelected(False)
                else:
                    item.setSelected(True)

        self.currentState = 'DEFAULT'

        super(Nodz, self).mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        """
        Save pressed key and apply shortcuts.

        Shortcuts are:
        DEL - Delete the selected nodes
        F - Focus view on the selection

        """
        if event.key() not in self.pressedKeys:
            self.pressedKeys.append(event.key())

        if event.key() == QtCore.Qt.Key_Delete:
            self._deleteSelectedNodes()

        if event.key() == QtCore.Qt.Key_F:
            self._focus()

        if event.key() == QtCore.Qt.Key_S:
            self._nodeSnap = True

        # Emit signal.
        self.signal_KeyPressed.emit(event.key())

    def keyReleaseEvent(self, event):
        """
        Clear the key from the pressed key list.

        """
        if event.key() == QtCore.Qt.Key_S:
            self._nodeSnap = False

        if event.key() in self.pressedKeys:
            self.pressedKeys.remove(event.key())

    # Sets node colours to the "Unrun" state (default red)
    def initializeNodeEvent(self, sender):
        nodes = self.scene().nodes.keys()
        for n in nodes:
            node = self.scene().nodes[n]
            node.nodePreset = "node_preset_initialized"
            node._createStyle(self.scene().views()[0].config)
            node.update()

    # Sets the currently active node's colours (default blue)
    def activateNodeEvent(self, sender, **kw):
        nodeID = kw["name"]
        nodes = self.scene().nodes.keys()
        for n in nodes:
            node = self.scene().nodes[n]
            if node.nodeId == nodeID:
                
                node.nodePreset = "node_preset_activated"
                node._createStyle(self.scene().views()[0].config)
                node.update()
        
    # Set a completed node's colours (default green)
    def completeNodeEvent(self, sender, **kw):
        nodeID = kw["name"]
        nodes = self.scene().nodes.keys()
        for n in nodes:
            node = self.scene().nodes[n]
            if node.nodeId == nodeID:
                node.nodePreset = "node_preset_completed"
                node._createStyle(self.scene().views()[0].config)
                node.update()
                
    def _initRubberband(self, position):
        """
        Initialize the rubber band at the given position.

        """
        self.rubberBandStart = position
        self.origin = position
        self.rubberband.setGeometry(QtCore.QRect(self.origin, QtCore.QSize()))
        self.rubberband.show()

    def _releaseRubberband(self):
        """
        Hide the rubber band and return the path.

        """
        painterPath = QtGui.QPainterPath()
        rect = self.mapToScene(self.rubberband.geometry())
        painterPath.addPolygon(rect)
        self.rubberband.hide()
        return painterPath

    def _focus(self):
        """
        Center on selected nodes or all of them if no active selection.

        """
        if self.scene().selectedItems():
            itemsArea = self._getSelectionBoundingbox()
            self.fitInView(itemsArea, QtCore.Qt.KeepAspectRatio)
        else:
            itemsArea = self.scene().itemsBoundingRect()
            self.fitInView(itemsArea, QtCore.Qt.KeepAspectRatio)

    def _getSelectionBoundingbox(self):
        """
        Return the bounding box of the selection.

        """
        bbx_min = None
        bbx_max = None
        bby_min = None
        bby_max = None
        bbw = 0
        bbh = 0
        for item in self.scene().selectedItems():
            pos = item.scenePos()
            x = pos.x()
            y = pos.y()
            w = x + item.boundingRect().width()
            h = y + item.boundingRect().height()

            # bbx min
            if bbx_min is None:
                bbx_min = x
            elif x < bbx_min:
                bbx_min = x
            # end if

            # bbx max
            if bbx_max is None:
                bbx_max = w
            elif w > bbx_max:
                bbx_max = w
            # end if

            # bby min
            if bby_min is None:
                bby_min = y
            elif y < bby_min:
                bby_min = y
            # end if

            # bby max
            if bby_max is None:
                bby_max = h
            elif h > bby_max:
                bby_max = h
            # end if
        # end if
        bbw = bbx_max - bbx_min
        bbh = bby_max - bby_min
        return QtCore.QRectF(QtCore.QRect(bbx_min, bby_min, bbw, bbh))

    def _deleteSelectedNodes(self):
        """
        Delete selected nodes.

        """
        selected_nodes = list()
        for node in self.scene().selectedItems():
            selected_nodes.append(node.nodeId)
            node._remove()

        # Emit signal.
        self.signal_NodeDeleted.emit(selected_nodes)

    def _returnSelection(self):
        """
        Wrapper to return selected items.

        """
        selected_nodes = list()
        if self.scene().selectedItems():
            for node in self.scene().selectedItems():
                selected_nodes.append(node.nodeId)

        # Emit signal.
        self.signal_NodeSelected.emit(selected_nodes)
        
    def _copySelectedNodes(self):
    
        newNodes = list()

        for node in self.scene().selectedItems():
            nt = node.type
            pos = QtCore.QPointF(node.pos().x() + 20, node.pos().y() + 20)
            
            settings = node.settings
            
            newNode = self.newNode(name = node.name,
                                   attrs = self.config['node_types'][nt],
                                   position = pos   , 
                                   settings = settings,
                                   type = nt,
                                   toolkit = node.toolkit)

            node.setSelected(False)
            newNode.setSelected(True)
            if newNode.type == "Custom":
               newNode.settings.initCustom()
    
    # Event activated when you try and close the program. 
    # If you have active nodes, it prompts you to save.
    # TODO - add state check so it only prompts when edits are made
    def checkClose(self):
        if len(self.scene().nodes) > 0:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText("Save before closing?")
            msg.setStandardButtons(QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Close | QtWidgets.QMessageBox.Cancel)
            
            ret = msg.exec_()
            
            # save
            if ret == 2048:
                self.saveGraphDialog()
            # Cancel
            elif ret == 4194304:
                return
    
        sys.exit()
     
    # Checks all nodes to see if a toolkit is in use
    # Makes it so that you cant disable a toolkit if nodes that use it exist
    def checkToolkitInUse(self, toolkit):
        nodes = self.scene().nodes.keys()
        for node in nodes:  
            if self.scene().nodes[node].toolkit == toolkit:
                return True
                
        return False
        
    # Open the settings UIs
    def openToolkit(self):
        self.toolkitUI.show()
        self.toolkitUI.activateWindow()
        
    def openHelp(self):
        self.helpUI.show()
        self.helpUI.activateWindow()
        
    def openGlobals(self):
        self.globalUI.show()
        self.globalUI.activateWindow()
        
    # Loop through all nodes and update their global variables
    # TODO - replace this with a signal
    def updateGlobals(self, globals):
        self.globals = globals
        for node in self.scene().nodes:
            n = self.scene().nodes[node]
            n.settingsWindow.updateGlobals(globals)
            
            # Used to update the contents of the Set Global and Get Global nodes' settings windows
            if n.type == "Set Global" or n.type == "Get Global":
                for i in range(0, n.settingsWindow.layout.rowCount()):
                    widget = n.settingsWindow.layout.itemAt(i, 1).widget()
                    if isinstance(widget, GlobalNodeComboBox):
                        widget.updateGlobals(globals)
    

    ##################################################################
    # API   
    ##################################################################

    def loadConfig(self, filePath):
        """
        Set a specific configuration for this instance of Nodz.

        :type  filePath: str.
        :param filePath: The path to the config file that you want to
                         use.

        """
        self.config = utils._loadConfig(filePath)
        customFile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "toolkits", "custom.json")
        custom = utils._loadConfig(customFile)
        self.config['node_types'] = custom['node_types']

    def reloadConfig(self, name = "", state = False):
        """ 
        reloads the list of toolkits and from that the 
        list of nodes available
        """
        
        if name == "custom":
            return
            
        nodes = self.scene().nodes.keys()
        
        # Checks if nodes are using the toolkit to be removed
        for node in nodes:  
            if self.scene().nodes[node].toolkit == name and state == False:
                QtWidgets.QMessageBox.critical(self, "WARNING", "Cannot remove toolkit in use")
                return False
        
        # Update the toolkit list
        if state == True: 
            if name not in self.toolkits:
                self.toolkits.append(name)
        else:
            if name in self.toolkits:
                self.toolkits.remove(name)
                
        # Make all globals editable. 
        # Globals from the config will be made uneditable as a part of addAutoRow
        self.globalUI.setRowsEditable()
      
        # Load default config
        self.loadConfig(defaultConfigPath)
        
        # Loop through toolkits and adds them to the node type list
        for tb in self.toolkits:
            path = os.path.normpath(os.path.join(self.toolkitUI.toolkitPaths[tb], "config.json"))
            cfg = utils._loadConfig(path)
            _types = cfg['node_types']
            types = {}
            # Rename the types for all nodes to include toolkit. This avoids duplication
            for key, type in _types.items():
                type["toolkit"] = tb
                # Load default preset if one not stated
                if "preset" not in type.keys():
                    type["preset"] = "node_default"
                types[tb+key] = type
            self.config['node_types'].update(types)
            if 'global_variables' in cfg:
                for gb in cfg['global_variables'].keys():
                    self.globalUI.addAutoRow(gb, cfg['global_variables'][gb])
        return True


    def initialize(self):
        """
        Setup the view's behavior.

        """
        # Setup view.
        config = self.config
        self.setRenderHint(QtGui.QPainter.Antialiasing, config['antialiasing'])
        self.setRenderHint(QtGui.QPainter.TextAntialiasing, config['antialiasing'])
        self.setRenderHint(QtGui.QPainter.HighQualityAntialiasing, config['antialiasing_boost'])
        self.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, config['smooth_pixmap'])
        self.setRenderHint(QtGui.QPainter.NonCosmeticDefaultPen, True)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.rubberband = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)

        # Setup scene.
        scene = NodeScene(self)
        sceneWidth = config['scene_width']
        sceneHeight = config['scene_height']
        scene.setSceneRect(0, 0, sceneWidth, sceneHeight)
        self.setScene(scene)
        # Connect scene node moved signal
        scene.signal_NodeMoved.connect(self.signal_NodeMoved)

        # Tablet zoom.
        self.previousMouseOffset = 0
        self.zoomDirection = 0
        self.zoomIncr = 0

        # Connect signals.
        self.scene().selectionChanged.connect(self._returnSelection)

    # NODES
    def createNode(self, type, name='default', preset='node_default', position=None, alternate=True, extended_attributes=None, nodeId=None, settings=None, toolkit=None):
        """
        Create a new node with a given name, position and color.

        :type  name: str.
        :param name: The name of the node. The name has to be unique
                     as it is used as a key to store the node object.

        :type  preset: str.
        :param preset: The name of graphical preset in the config file.

        :type  position: QtCore.QPoint.
        :param position: The position of the node once created. If None,
                         it will be created at the center of the scene.

        :type  alternate: bool.
        :param alternate: The attribute color alternate state, if True,
                          every 2 attribute the color will be slightly
                          darker.

        :return : The created node

        """
        # Check for name clashes
        if nodeId == None:
            nodeId = uuid.uuid4().hex
            
        # Get the toolkit path
        tkPath = ""
        if "settingsFile" in settings.keys():
            if toolkit != "custom":
                tkPath = os.path.normpath(os.path.join(self.toolkitUI.toolkitPaths[toolkit], settings["settingsFile"] + ".py"))
            else:
                tkPath = os.path.normpath(settings["settingsFile"])

        if nodeId in self.scene().nodes.keys():
            print('A node with the same name already exists : {0}'.format(name))
            print('Node creation aborted !')
            return
        else:
            nodeItem = NodeItem(nodeId=nodeId, 
                                name=name, 
                                alternate=alternate, 
                                preset=preset,
                                config=self.config, 
                                extended_attributes=extended_attributes,
                                settings=settings, 
                                type=type, 
                                toolkit=toolkit, 
                                toolkitPath=tkPath,
                                globals = self.globals)

            # Store node in scene.
            self.scene().nodes[nodeId] = nodeItem

            if not position:
                # Get the center of the view.
                position = self.mapToScene(self.viewport().rect().center())

            # Set node position.
            self.scene().addItem(nodeItem)
            #nodeItem.setPos(position - nodeItem.nodeCenter)
            nodeItem.setPos(position)

            # Emit signal.
            self.signal_NodeCreated.emit(nodeId)
            
            # Update the global listbox if the node is of that type
            if type == "Get Global" or type == "Set Global":
                self.globalUI.genGlobals()

            return nodeItem

    def deleteNode(self, node):
        """
        Delete the specified node from the view.

        :type  node: class.
        :param node: The node instance that you want to delete.

        """
        if not node in self.scene().nodes.values():
            print('Node object does not exist !')
            print('Node deletion aborted !')
            return

        if node in self.scene().nodes.values():
            nodeName = node.nodeId
            node._remove()

            # Emit signal.
            self.signal_NodeDeleted.emit([nodeName])

    def editNode(self, node, newName=None):
        """
        Rename an existing node.

        :type  node: class.
        :param node: The node instance that you want to delete.

        :type  newName: str.
        :param newName: The new name for the given node.

        """
        if not node in self.scene().nodes.values():
            print('Node object does not exist !')
            print('Node edition aborted !')
            return

        oldName = node.name


        node.name = newName

        # Replace node data.
        #self.scene().nodes[newName] = self.scene().nodes[oldName]
        #self.scene().nodes.pop(oldName)

        # Store new node name in the connections
        #if node.sockets:
        #    for socket in node.sockets.values():
        #        for connection in socket.connections:
        #           connection.socketNode = newName

        #if node.plugs:
        #    for plug in node.plugs.values():
        #        for connection in plug.connections:
        #            connection.plugNode = newName

        node.update()

        # Emit signal.
        self.signal_NodeEdited.emit(oldName, newName)


    # ATTRS
    def createAttribute(self, node, name='default', index=-1, preset='attr_default', plug=True, socket=True, dataType=None):
        """
        Create a new attribute with a given name.

        :type  node: class.
        :param node: The node instance that you want to delete.

        :type  name: str.
        :param name: The name of the attribute. The name has to be
                     unique as it is used as a key to store the node
                     object.

        :type  index: int.
        :param index: The index of the attribute in the node.

        :type  preset: str.
        :param preset: The name of graphical preset in the config file.

        :type  plug: bool.
        :param plug: Whether or not this attribute can emit connections.

        :type  socket: bool.
        :param socket: Whether or not this attribute can receive
                       connections.

        :type  dataType: type.
        :param dataType: Type of the data represented by this attribute
                         in order to highlight attributes of the same
                         type while performing a connection.

        """
        if not node in self.scene().nodes.values():
            print('Node object does not exist !')
            print('Attribute creation aborted !')
            return

        if name in node.attrs:
            print('An attribute with the same name already exists : {0}'.format(name))
            print('Attribute creation aborted !')
            return

        node._createAttribute(name=name, index=index, preset=preset, plug=plug, socket=socket, dataType=dataType)

        # Emit signal.
        self.signal_AttrCreated.emit(node.name, index)

    def deleteAttribute(self, node, index):
        """
        Delete the specified attribute.

        :type  node: class.
        :param node: The node instance that you want to delete.

        :type  index: int.
        :param index: The index of the attribute in the node.

        """
        if not node in self.scene().nodes.values():
            print('Node object does not exist !')
            print('Attribute deletion aborted !')
            return

        node._deleteAttribute(index)

        # Emit signal.
        self.signal_AttrDeleted.emit(node.name, index)

    def editAttribute(self, node, index, newName=None, newIndex=None):
        """
        Edit the specified attribute.

        :type  node: class.
        :param node: The node instance that you want to delete.

        :type  index: int.
        :param index: The index of the attribute in the node.

        :type  newName: str.
        :param newName: The new name for the given attribute.

        :type  newIndex: int.
        :param newIndex: The index for the given attribute.

        """
        if not node in self.scene().nodes.values():
            print('Node object does not exist !')
            print('Attribute creation aborted !')
            return

        if newName != None:
            if newName in node.attrs:
                print('An attribute with the same name already exists : {0}'.format(newName))
                print('Attribute edition aborted !')
                return
            else:
                oldName = node.attrs[index]

            # Rename in the slot item(s).
            if node.attrsData[oldName]['plug']:
                node.plugs[oldName].attribute = newName
                node.plugs[newName] = node.plugs[oldName]
                node.plugs.pop(oldName)
                for connection in node.plugs[newName].connections:
                    connection.plugAttr = newName

            if node.attrsData[oldName]['socket']:
                node.sockets[oldName].attribute = newName
                node.sockets[newName] = node.sockets[oldName]
                node.sockets.pop(oldName)
                for connection in node.sockets[newName].connections:
                    connection.socketAttr = newName

            # Replace attribute data.
            node.attrsData[oldName]['name'] = newName
            node.attrsData[newName] = node.attrsData[oldName]
            node.attrsData.pop(oldName)
            node.attrs[index] = newName

        if isinstance(newIndex, int):
            utils._swapListIndices(node.attrs, index, newIndex)

            # Refresh connections.
            for plug in node.plugs.values():
                plug.update()
                if plug.connections:
                    for connection in plug.connections:
                        if isinstance(connection.source, PlugItem):
                            connection.source = plug
                            connection.source_point = plug.center()
                        else:
                            connection.target = plug
                            connection.target_point = plug.center()
                        if newName:
                            connection.plugAttr = newName
                        connection.updatePath()

            for socket in node.sockets.values():
                socket.update()
                if socket.connections:
                    for connection in socket.connections:
                        if isinstance(connection.source, SocketItem):
                            connection.source = socket
                            connection.source_point = socket.center()
                        else:
                            connection.target = socket
                            connection.target_point = socket.center()
                        if newName:
                            connection.socketAttr = newName
                        connection.updatePath()

            self.scene().update()

        node.update()

        # Emit signal.
        if newIndex:
            self.signal_AttrEdited.emit(node.name, index, newIndex)
        else:
            self.signal_AttrEdited.emit(node.name, index, index)


    # GRAPH
    def saveGraph(self, filePath='path'):
        """
        Get all the current graph infos and store them in a .json file
        at the given location.

        :type  filePath: str.
        :param filePath: The path where you want to save your graph at.

        """
        data = dict()

        data["TOOLKITS"] = self.toolkitUI.toolkitPaths

        # Store nodes data.
        data['NODES'] = dict()

        nodes = self.scene().nodes.keys()

        for node in nodes:
        
            nodeInst = self.scene().nodes[node]
            
            # Make sure settings are up to date before saving
            nodeInst.settingsWindow.genSettings()
            
            name = nodeInst.name
            preset = "node_default"
            nodeAlternate = nodeInst.alternate
            toolkit = nodeInst.toolkit
            variables = nodeInst.variables         
            file = self.config['node_types'][nodeInst.type]['file']
            
            #if nodeInst.toolkit == 'default':
            #    nodeType = nodeInst.type 
            #else: 
            nodeType = nodeInst.type[len(toolkit):]
                
            if nodeInst.toolkit == 'custom':
                nodeType = nodeInst.type
                file = nodeInst.settingsWindow.customFilePath
            
            data['NODES'][node] = { 'name': name,
                                    'type': nodeType,
                                    'file': file,
                                    'toolkit' : toolkit,
                                    'preset': preset,
                                    'position': [nodeInst.pos().x(), nodeInst.pos().y()],
                                    'alternate': nodeAlternate,
                                    'attributes': [],
                                    'settings': nodeInst.settings,
                                    'variables' : variables}

            attrs = nodeInst.attrs
            for attr in attrs:
                attrData = nodeInst.attrsData[attr]

                # serialize dataType if needed.
                if isinstance(attrData['dataType'], type):
                    attrData['dataType'] = str(attrData['dataType'])

                data['NODES'][node]['attributes'].append(attrData)


        # Store connections data.
        data['CONNECTIONS'] = self.evaluateGraph()
        data['GLOBALS'] = self.globalUI.genGlobals()


        # Save data.
        try:
            utils._saveData(filePath=filePath, data=data)
        except:
            print('Invalid path : {0}'.format(filePath))
            print('Save aborted !')
            return False

        self.currentFileName = filePath
        
        # Emit signal.
        self.signal_GraphSaved.emit()

    def newNode(self,name,attrs,position,settings,type,toolkit):
        node = self.createNode(name=name,preset=attrs['preset'],position=position, settings = settings, type = type, toolkit = toolkit)

        for attr in attrs['attributes']:
        
            # Parse the more dev-friendly attribute properties for custom toolkits
            if 'connection' in attrs['attributes'][attr].keys():
                if attrs['attributes'][attr]['connection'] == "input":
                    attrs['attributes'][attr]['plug'] = False
                    attrs['attributes'][attr]['socket'] = True
                elif attrs['attributes'][attr]['connection'] == "output":
                    attrs['attributes'][attr]['plug'] = True
                    attrs['attributes'][attr]['socket'] = False
                    
            # Set default for preset
            if 'preset' in attrs['attributes'][attr].keys():
                preset = attrs['attributes'][attr]['preset']
            else:
                preset = "attr_preset_1"
                
            # Set default for index
            if 'index' in attrs['attributes'][attr].keys():
                index = attrs['attributes'][attr]['index']
            else:
                index = -1
                
            self.createAttribute(node,name=attr,index=index,preset=preset,plug=attrs['attributes'][attr]['plug'],socket=attrs['attributes'][attr]['socket'],dataType=attrs['attributes'][attr]['type'])
            
        return node

    # Shows prompt to load a flowchart
    def loadGraphDialog(self):
        dialog = QtWidgets.QFileDialog.getOpenFileName(directory='.', filter="JSON files (*.json)")
        if (dialog[0] != ''):
            if (not self.clearGraph()):
                return
            self.loadGraph(filePath=dialog[0])

    # Shows a prompt to save a flowchart
    def saveGraphDialog(self):
        dialog = QtWidgets.QFileDialog.getSaveFileName(directory='.', filter="JSON files (*.json)")
        if (dialog != ''):
            self.saveGraph(filePath=dialog[0])

    def loadGraph(self, filePath='path'):
        """
        Get all the stored info from the .json file at the given location
        and recreate the graph as saved.

        :type  filePath: str.
        :param filePath: The path where you want to load your graph from.

        """
        # Load data.

        if os.path.exists(filePath):
            data = utils._loadData(filePath=filePath)
        else:
            print('Invalid path : {0}'.format(filePath))
            print('Load aborted !')
            return False
           
           
        self.toolkits = []
        self.globalUI.clearTable()

        # Apply nodes data.
        nodesData = data['NODES']
        nodeIds = nodesData.keys()

        for nodeId in nodeIds:
            name = nodesData[nodeId]['name']
            nodeType = nodesData[nodeId]['type']
            preset = nodesData[nodeId]['preset']
            position = nodesData[nodeId]['position']
            position = QtCore.QPointF(position[0], position[1])
            alternate = nodesData[nodeId]['alternate']
            settings = nodesData[nodeId]['settings']
            toolkit = nodesData[nodeId]['toolkit']
            
            # Make sure that the toolkit exists in the toolkit manager
            if not self.toolkitUI.checkAdded(toolkit):
                return

            if toolkit != "custom":
                nodeType = toolkit+nodeType

            node = self.createNode( nodeId=nodeId,
                                    name=name,
                                    type=nodeType,
                                    preset=preset,
                                    position=position,
                                    alternate=alternate,
                                    settings=settings,
                                    toolkit=toolkit)
            
               
            # Apply attributes data.
            attrsData = nodesData[nodeId]['attributes']

            for attrData in attrsData:
                index = attrsData.index(attrData)
                name = attrData['name']
                plug = attrData['plug']
                socket = attrData['socket']
                preset = attrData['preset']
                dataType = attrData['dataType']

                # un-serialize data type if needed
                if (isinstance(dataType, str) and dataType.find('<') == 0):
                    dataType = eval(str(dataType.split('\'')[1]))

                self.createAttribute(node=node,
                                     name=name,
                                     index=index,
                                     preset=preset,
                                     plug=plug,
                                     socket=socket,
                                     dataType=dataType)

        # Apply connections data.
        connectionsData = data['CONNECTIONS']

        for connection in connectionsData:
            source = connection[0]
            sourceNode = source.split('.')[0]
            sourceAttr = source.split('.')[1]

            target = connection[1]
            targetNode = target.split('.')[0]
            targetAttr = target.split('.')[1]

            self.createConnection(sourceNode, sourceAttr,
                                  targetNode, targetAttr)          
        
        # Load global variables
        if "GLOBALS" in data.keys(): 
            self.globalUI.loadGlobals(data["GLOBALS"])
        self.globalUI.genGlobals()
        
        self.scene().update()
        self.helpUI.buildToolkitHelp()
        
        self.currentFileName = filePath

        # Emit signal.
        self.signal_GraphLoaded.emit()
        print("Data successfully loaded !")

    def createConnection(self, sourceNode, sourceAttr, targetNode, targetAttr):
        """
        Create a manual connection.

        :type  sourceNode: str.
        :param sourceNode: Node that emits the connection.

        :type  sourceAttr: str.
        :param sourceAttr: Attribute that emits the connection.

        :type  targetNode: str.
        :param targetNode: Node that receives the connection.

        :type  targetAttr: str.
        :param targetAttr: Attribute that receives the connection.

        """
        plug = self.scene().nodes[sourceNode].plugs[sourceAttr]
        socket = self.scene().nodes[targetNode].sockets[targetAttr]

        connection = ConnectionItem(plug.center(), socket.center(), plug, socket)

        connection.plugNode = plug.parentItem().nodeId
        connection.plugAttr = plug.attribute
        connection.socketNode = socket.parentItem().nodeId
        connection.socketAttr = socket.attribute

        plug.connect(socket, connection)
        socket.connect(plug, connection)

        connection.updatePath()

        self.scene().addItem(connection)

        return connection

    def evaluateGraph(self, tuples=False):
        """
        Create a list of connection tuples.
        [("sourceNode.attribute", "TargetNode.attribute"), ...]

        """
        scene = self.scene()

        data = list()

        for item in scene.items():
            if not isinstance(item, ConnectionItem):
                continue

            connection = item

            cdata = connection._outputConnectionData()

            if tuples:
                pair = cdata
            else:
                plugData, socketData = cdata
                pair = ("{0}.{1}".format(*plugData),
                        "{0}.{1}".format(*socketData))
            data.append(pair)

        # Emit Signal
        self.signal_GraphEvaluated.emit()

        return data

    def clearGraph(self):
        """
        Clear the graph.

        """
        if (len(self.scene().nodes)>0):
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setWindowTitle("Clear Diagram")
            msg.setText("Are you sure?")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            msg.setDefaultButton(QtWidgets.QMessageBox.Cancel)
            retval = msg.exec_()
            if (retval == QtWidgets.QMessageBox.Ok):
                self.scene().clear()
                self.scene().nodes = dict()

                # Emit signal.
                self.signal_GraphCleared.emit()
                return True
            else:
                return False
        else:
            self.scene().clear()
            self.scene().nodes = dict()

            # Emit signal.
            self.signal_GraphCleared.emit()
            return True

    ##################################################################
    # END API
    ##################################################################


class NodeScene(QtWidgets.QGraphicsScene):

    """
    The scene displaying all the nodes.

    """
    signal_NodeMoved = QtCore.pyqtSignal(str, object)

    def __init__(self, parent):
        """
        Initialize the class.

        """
        super(NodeScene, self).__init__(parent)
        #self.setAcceptDrops(True)

        # General.
        self.gridSize = parent.config['grid_size']

        # Nodes storage.
        self.nodes = dict()

    def dragEnterEvent(self, event):
        """
        Make the dragging of nodes into the scene possible.

        """
        event.setDropAction(QtCore.Qt.MoveAction)
        event.accept()

    def dragMoveEvent(self, event):
        """
        Make the dragging of nodes into the scene possible.

        """
        event.setDropAction(QtCore.Qt.MoveAction)
        event.accept()

    def dropEvent(self, event):
        """
        Create a node from the dropped item.

        """
        # Emit signal.
        self.parent().signal_Dropped.emit(event.scenePos())
        print("DROP EVENT")
        print(event.mimeData().text())
        print(event.scenePos())
        print("")

        event.accept()

    def drawBackground(self, painter, rect):
        """
        Draw a grid in the background.

        """

        background_brush = QtGui.QBrush( QtGui.QColor(0,0,0), QtCore.Qt.SolidPattern)
        painter.fillRect(rect, background_brush)

        if self.views()[0].gridVisToggle:
            leftLine = rect.left() - rect.left() % self.gridSize
            topLine = rect.top() - rect.top() % self.gridSize
            lines = list()

            i = int(leftLine)
            while i < int(rect.right()):
                lines.append(QtCore.QLineF(i, rect.top(), i, rect.bottom()))
                i += self.gridSize

            u = int(topLine)
            while u < int(rect.bottom()):
                lines.append(QtCore.QLineF(rect.left(), u, rect.right(), u))
                u += self.gridSize

            self.pen = QtGui.QPen()
            config = self.parent().config
            self.pen.setColor(utils._convertDataToColor(config['grid_color']))
            self.pen.setWidth(0)
            painter.setPen(self.pen)
            painter.drawLines(lines)

    def updateScene(self):
        """
        Update the connections position.

        """
        for connection in [i for i in self.items() if isinstance(i, ConnectionItem)]:
            connection.target_point = connection.target.center()
            connection.source_point = connection.source.center()
            connection.updatePath()


class NodeItem(QtWidgets.QGraphicsItem):

    """
    A graphic representation of a node containing attributes.

    """

    def __init__(self, nodeId, name, alternate, preset, config, extended_attributes=None, settings=None, type=None, toolkit=None, toolkitPath=None, globals=None):
        """
        Initialize the class.

        :type  name: str.
        :param name: The name of the node. The name has to be unique
                     as it is used as a key to store the node object.

        :type  alternate: bool.
        :param alternate: The attribute color alternate state, if True,
                          every 2 attribute the color will be slightly
                          darker.

        :type  preset: str.
        :param preset: The name of graphical preset in the config file.

        """
        super(NodeItem, self).__init__()

        self.setZValue(1)

        # Storage
        self.nodeId = nodeId
        self.name = name
        self.alternate = alternate
        self.nodePreset = preset
        self.attrPreset = None
        self.type = type
        self.toolkit = toolkit

        # Attributes storage.
        self.attrs = list()
        self.attrsData = dict()
        self.attrCount = 0
        self.currentDataType = None

        self.plugs = dict()
        self.sockets = dict()
        
        self.settings = {}
        self.variables = dict()

        # Extended attributes
        self.extended_attributes = {}
        if extended_attributes:
            self.extended_attributes = extended_attributes

        # Methods.
        self._createStyle(config)
        
        # Load custom settings window
        if "settingsFile" in settings.keys():  
            spec = importlib.util.spec_from_file_location("custom", toolkitPath)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            
            cls = getattr(mod, settings["settingsClass"])
            self.settingsWindow = cls(self, settings)
            
        # Load default settings window based on JSON
        else:
            self.settingsWindow = SettingsItem(self, settings)
            
        self.settingsWindow.updateGlobals(globals)

    @property
    def height(self):
        """
        Increment the final height of the node every time an attribute
        is created.

        """
        if self.attrCount > 0:
            return int(self.baseHeight +
                    self.attrHeight * self.attrCount +
                    self.border +
                    0.5 * self.radius)
        else:
            return self.baseHeight

    @property
    def pen(self):
        """
        Return the pen based on the selection state of the node.

        """
        if self.isSelected():
            return self._penSel
        else:
            return self._pen

    def _createStyle(self, config):
        """
        Read the node style from the configuration file.

        """
        self.setAcceptHoverEvents(True)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable)

        # Dimensions.
        self.baseWidth  = int(config['node_width'])
        self.baseHeight = int(config['node_height'])
        self.attrHeight = config['node_attr_height']
        self.border = config['node_border']
        self.radius = config['node_radius']

        self.nodeCenter = QtCore.QPointF()
        self.nodeCenter.setX(self.baseWidth / 2.0)
        self.nodeCenter.setY(self.height / 2.0)

        self._brush = QtGui.QBrush()
        self._brush.setStyle(QtCore.Qt.SolidPattern)
        self._brush.setColor(utils._convertDataToColor(config[self.nodePreset]['bg']))

        self._pen = QtGui.QPen()
        self._pen.setStyle(QtCore.Qt.SolidLine)
        self._pen.setWidth(self.border)
        self._pen.setColor(utils._convertDataToColor(config[self.nodePreset]['border']))

        self._penSel = QtGui.QPen()
        self._penSel.setStyle(QtCore.Qt.SolidLine)
        self._penSel.setWidth(self.border)
        self._penSel.setColor(utils._convertDataToColor(config[self.nodePreset]['border_sel']))

        self._textPen = QtGui.QPen()
        self._textPen.setStyle(QtCore.Qt.SolidLine)
        self._textPen.setColor(utils._convertDataToColor(config[self.nodePreset]['text']))

        self._nodeTextFont = QtGui.QFont(config['node_font'], config['node_font_size'], QtGui.QFont.Bold)
        self._attrTextFont = QtGui.QFont(config['attr_font'], config['attr_font_size'], QtGui.QFont.Normal)

        self._attrBrush = QtGui.QBrush()
        self._attrBrush.setStyle(QtCore.Qt.SolidPattern)

        self._attrBrushAlt = QtGui.QBrush()
        self._attrBrushAlt.setStyle(QtCore.Qt.SolidPattern)

        self._attrPen = QtGui.QPen()
        self._attrPen.setStyle(QtCore.Qt.SolidLine)

    def _createAttribute(self, name, index, preset, plug, socket, dataType):
        """
        Create an attribute by expanding the node, adding a label and
        connection items.

        :type  name: str.
        :param name: The name of the attribute. The name has to be
                     unique as it is used as a key to store the node
                     object.

        :type  index: int.
        :param index: The index of the attribute in the node.

        :type  preset: str.
        :param preset: The name of graphical preset in the config file.

        :type  plug: bool.
        :param plug: Whether or not this attribute can emit connections.

        :type  socket: bool.
        :param socket: Whether or not this attribute can receive
                       connections.

        :type  dataType: type.
        :param dataType: Type of the data represented by this attribute
                         in order to highlight attributes of the same
                         type while performing a connection.

        """
        if name in self.attrs:
            print('An attribute with the same name already exists on this node : {0}'.format(name))
            print('Attribute creation aborted !')
            return

        self.attrPreset = preset

        # Create a plug connection item.
        if plug:
            plugInst = PlugItem(parent=self,
                                attribute=name,
                                index=self.attrCount,
                                preset=preset,
                                dataType=dataType)

            self.plugs[name] = plugInst

        # Create a socket connection item.
        if socket:
            socketInst = SocketItem(parent=self,
                                    attribute=name,
                                    index=self.attrCount,
                                    preset=preset,
                                    dataType=dataType)

            self.sockets[name] = socketInst

        self.attrCount += 1

        # Add the attribute based on its index.
        if index == -1 or index > self.attrCount:
            self.attrs.append(name)
        else:
            self.attrs.insert(index, name)

        # Store attr data.
        self.attrsData[name] = {'name': name,
                                'socket': socket,
                                'plug': plug,
                                'preset': preset,
                                'dataType': dataType}

        # Update node height.
        self.update()

    def _deleteAttribute(self, index):
        """
        Remove an attribute by reducing the node, removing the label
        and the connection items.       

        :type  index: int.
        :param index: The index of the attribute in the node.

        """
        name = self.attrs[index]

        # Remove socket and its connections.
        if name in self.sockets.keys():
            for connection in self.sockets[name].connections:
                connection._remove()

            self.scene().removeItem(self.sockets[name])
            self.sockets.pop(name)

        # Remove plug and its connections.
        if name in self.plugs.keys():
            for connection in self.plugs[name].connections:
                connection._remove()

            self.scene().removeItem(self.plugs[name])
            self.plugs.pop(name)

        # Reduce node height.
        if self.attrCount > 0:
            self.attrCount -= 1

        # Remove attribute from node.
        if name in self.attrs:
            self.attrs.remove(name)

        self.update()

    def _remove(self):
        """
        Remove this node instance from the scene.

        Make sure that all the connections to this node are also removed
        in the process

        """
        self.scene().nodes.pop(self.nodeId)

        # Remove all sockets connections.
        for socket in self.sockets.values():
            while len(socket.connections)>0:
                socket.connections[0]._remove()

        # Remove all plugs connections.
        for plug in self.plugs.values():
            while len(plug.connections)>0:
                plug.connections[0]._remove()

        # Remove node.
        scene = self.scene()
        scene.removeItem(self)
        scene.update()

    def boundingRect(self):
        """
        The bounding rect based on the width and height variables.

        """
        rect = QtCore.QRect(0, 0, self.baseWidth, self.height)
        rect = QtCore.QRectF(rect)
        return rect

    def shape(self):
        """
        The shape of the item.

        """
        path = QtGui.QPainterPath()
        path.addRect(self.boundingRect())
        return path

    def paint(self, painter, option, widget):
        """
        Paint the node and attributes.

        """
        # Node base.
        painter.setBrush(self._brush)
        painter.setPen(self.pen)

        painter.drawRoundedRect(0, 0,
                                self.baseWidth,
                                self.height,
                                self.radius,
                                self.radius)

        # Node label.   
        painter.setPen(self._textPen)
        painter.setFont(self._nodeTextFont)

        metrics = QtGui.QFontMetrics(painter.font())
        text_width = metrics.boundingRect(self.name).width() + 14
        text_height = metrics.boundingRect(self.name).height() + 14
        margin = int((text_width - self.baseWidth) * 0.5)
        textRect = QtCore.QRect(-margin,
                                -text_height,
                                text_width,
                                text_height)

        painter.drawText(textRect,
                         QtCore.Qt.AlignCenter,
                         self.name)


        # Attributes.
        offset = 0

        for attr in self.attrs:
            nodzInst = self.scene().views()[0]
            config = nodzInst.config

            # Attribute rect.
            rect = QtCore.QRect(int(self.border / 2),
                                self.baseHeight - self.radius + offset,
                                self.baseWidth - self.border,
                                self.attrHeight)



            attrData = self.attrsData[attr]
            name = attr

            preset = attrData['preset']


            # Attribute base.
            self._attrBrush.setColor(utils._convertDataToColor(config[preset]['bg']))
            if self.alternate:
                self._attrBrushAlt.setColor(utils._convertDataToColor(config[preset]['bg'], True, config['alternate_value']))

            self._attrPen.setColor(utils._convertDataToColor([0, 0, 0, 0]))
            painter.setPen(self._attrPen)
            painter.setBrush(self._attrBrush)
            if (offset / self.attrHeight) % 2:
                painter.setBrush(self._attrBrushAlt)

            painter.drawRect(rect)

            # Attribute label.
            painter.setPen(utils._convertDataToColor(config[preset]['text']))
            painter.setFont(self._attrTextFont)

            # Search non-connectable attributes.
            if nodzInst.drawingConnection:
                if self == nodzInst.currentHoveredNode:
                    matchingTypes = False
                    if isinstance(nodzInst.sourceSlot.dataType, str):
                        matchingTypes = nodzInst.sourceSlot.dataType not in attrData['dataType']         
                    if isinstance(attrData['dataType'], str):
                        matchingTypes = attrData['dataType'] not in nodzInst.sourceSlot.dataType
                        
                    if (matchingTypes or (nodzInst.sourceSlot.slotType == 'plug' and attrData['socket'] == False) or (nodzInst.sourceSlot.slotType == 'socket' and attrData['plug'] == False)) and (('file' not in attrData['dataType']) and ("file" not in nodzInst.sourceSlot.dataType)):
                        # Set non-conn  ectable attributes color.
                        painter.setPen(utils._convertDataToColor(config['non_connectable_color']))

            textRect = QtCore.QRect(rect.left() + self.radius,
                                     rect.top(),
                                     rect.width() - 2*self.radius,
                                     rect.height())
            if(self.attrsData[attr]['plug'] and self.attrsData[attr]['socket']):
                painter.drawText(textRect, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter, name)
            elif(self.attrsData[attr]['plug']):
                painter.drawText(textRect, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight, name)
            elif(self.attrsData[attr]['socket']):
                painter.drawText(textRect, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft, name)
            else:
                painter.drawText(textRect, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter, name)
            offset += self.attrHeight

    def mousePressEvent(self, event):
        """
        Keep the selected node on top of the others.

        """
        nodes = self.scene().nodes
        for node in nodes.values():
            node.setZValue(1)

        for item in self.scene().items():
            if isinstance(item, ConnectionItem):
                item.setZValue(1)

        self.setZValue(2)

        super(NodeItem, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
        .

        """
        if self.scene().views()[0].gridVisToggle:
            if self.scene().views()[0].gridSnapToggle or self.scene().views()[0]._nodeSnap:
                gridSize = self.scene().gridSize

                currentPos = self.mapToScene(event.pos().x() - self.baseWidth / 2,
                                             event.pos().y() - self.height / 2)

                snap_x = (round(currentPos.x() / gridSize) * gridSize) - gridSize/4
                snap_y = (round(currentPos.y() / gridSize) * gridSize) - gridSize/4
                snap_pos = QtCore.QPointF(snap_x, snap_y)
                self.setPos(snap_pos)

                self.scene().updateScene()
            else:
                self.scene().updateScene()
                super(NodeItem, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """
        .

        """
        # Emit node moved signal.
        self.scene().signal_NodeMoved.emit(self.name, self.pos())
        super(NodeItem, self).mouseReleaseEvent(event)

    def hoverLeaveEvent(self, event):
        """
        .

        """
        nodzInst = self.scene().views()[0]

        for item in nodzInst.scene().items():
            if isinstance(item, ConnectionItem):
                item.setZValue(0)

        super(NodeItem, self).hoverLeaveEvent(event)
        
    def mouseDoubleClickEvent(self, event):
        self.settingsWindow.show()
        self.settingsWindow.activateWindow()


class SlotItem(QtWidgets.QGraphicsItem):

    """
    The base class for graphics item representing attributes hook.

    """

    def __init__(self, parent, attribute, preset, index, dataType):
        """
        Initialize the class.

        :param parent: The parent item of the slot.
        :type  parent: QtWidgets.QGraphicsItem instance.

        :param attribute: The attribute associated to the slot.
        :type  attribute: String.

        :param index: int.
        :type  index: The index of the attribute in the node.

        :type  preset: str.
        :param preset: The name of graphical preset in the config file.

        :param dataType: The data type associated to the attribute.
        :type  dataType: Type.

        """
        super(SlotItem, self).__init__(parent)

        # Status.
        self.setAcceptHoverEvents(True)

        # Storage.
        self.slotType = None
        self.attribute = attribute
        self.preset = preset
        self.index = index
        self.dataType = dataType
        if isinstance(dataType, str):
            self.setToolTip(dataType)
        else:
            self.setToolTip("/".join(dataType))

        # Style.
        self.brush = QtGui.QBrush()
        self.brush.setStyle(QtCore.Qt.SolidPattern)

        self.pen = QtGui.QPen()
        self.pen.setStyle(QtCore.Qt.SolidLine)

        # Connections storage.
        self.connected_slots = list()
        self.newConnection = None
        self.connections = list()

    def mousePressEvent(self, event):
        """
        Start the connection process.

        """
        if event.button() == QtCore.Qt.LeftButton:
            self.newConnection = ConnectionItem(self.center(),
                                                self.mapToScene(event.pos()),
                                                self,
                                                None)

            self.connections.append(self.newConnection)
            self.scene().addItem(self.newConnection)

            nodzInst = self.scene().views()[0]
            nodzInst.drawingConnection = True
            nodzInst.sourceSlot = self
            nodzInst.currentDataType = self.dataType

        else:
            super(SlotItem, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """
        Update the new connection's end point position.

        """
        nodzInst = self.scene().views()[0]
        config = nodzInst.config
        if nodzInst.drawingConnection:
            mbb = utils._createPointerBoundingBox(pointerPos=event.scenePos().toPoint(),
                                                  bbSize=config['mouse_bounding_box'])

            # Get nodes in pointer's bounding box.
            targets = self.scene().items(mbb)

            if any(isinstance(target, NodeItem) for target in targets):
                if self.parentItem() not in targets:
                    for target in targets:
                        if isinstance(target, NodeItem):
                            nodzInst.currentHoveredNode = target
            else:
                nodzInst.currentHoveredNode = None

            # Set connection's end point.
            self.newConnection.target_point = self.mapToScene(event.pos())
            self.newConnection.updatePath()
        else:
            super(SlotItem, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """
        Apply the connection if target_slot is valid.

        """
        nodzInst = self.scene().views()[0]
        if event.button() == QtCore.Qt.LeftButton:
            nodzInst.drawingConnection = False
            nodzInst.currentDataType = None

            target = self.scene().itemAt(event.scenePos().toPoint(), QtGui.QTransform())

            if not isinstance(target, SlotItem):
                self.newConnection._remove()
                super(SlotItem, self).mouseReleaseEvent(event)
                return

            if target.accepts(self):
                self.newConnection.target = target
                self.newConnection.source = self
                self.newConnection.target_point = target.center()
                self.newConnection.source_point = self.center()

                # Perform the ConnectionItem.
                self.connect(target, self.newConnection)
                target.connect(self, self.newConnection)

                self.newConnection.updatePath()
            else:
                self.newConnection._remove()
        else:
            super(SlotItem, self).mouseReleaseEvent(event)

        nodzInst.currentHoveredNode = None

    def shape(self):
        """
        The shape of the Slot is a circle.

        """
        path = QtGui.QPainterPath()
        path.addRect(self.boundingRect())
        return path

    def paint(self, painter, option, widget):
        """
        Paint the Slot.

        """
        painter.setBrush(self.brush)
        painter.setPen(self.pen)

        nodzInst = self.scene().views()[0]
        config = nodzInst.config
        if nodzInst.drawingConnection:
            if self.parentItem() == nodzInst.currentHoveredNode:
                painter.setBrush(utils._convertDataToColor(config['non_connectable_color']))
                    
                matchingTypes = False
                if isinstance(nodzInst.sourceSlot.dataType, str):
                    matchingTypes = nodzInst.sourceSlot.dataType not in self.dataType
                if isinstance(self.dataType, str):
                    matchingTypes = self.dataType not in nodzInst.sourceSlot.dataType 
                    
                if ((self.slotType == nodzInst.sourceSlot.slotType or matchingTypes)
                    and ("file" not in self.dataType) and ("file" not in nodzInst.sourceSlot.dataType)):
                    painter.setBrush(utils._convertDataToColor(config['non_connectable_color']))
                else:
                    _penValid = QtGui.QPen()
                    _penValid.setStyle(QtCore.Qt.SolidLine)
                    _penValid.setWidth(2)
                    _penValid.setColor(QtGui.QColor(255, 255, 255, 255))
                    painter.setPen(_penValid)
                    painter.setBrush(self.brush)

        painter.drawEllipse(self.boundingRect())

    def center(self):
        """
        Return The center of the Slot.

        """
        rect = self.boundingRect()
        center = QtCore.QPointF(rect.x() + rect.width() * 0.5,
                                rect.y() + rect.height() * 0.5)

        return self.mapToScene(center)


class PlugItem(SlotItem):

    """
    A graphics item representing an attribute out hook.

    """

    def __init__(self, parent, attribute, index, preset, dataType):
        """
        Initialize the class.

        :param parent: The parent item of the slot.
        :type  parent: QtWidgets.QGraphicsItem instance.

        :param attribute: The attribute associated to the slot.
        :type  attribute: String.

        :param index: int.
        :type  index: The index of the attribute in the node.

        :type  preset: str.
        :param preset: The name of graphical preset in the config file.

        :param dataType: The data type associated to the attribute.
        :type  dataType: Type.

        """
        super(PlugItem, self).__init__(parent, attribute, preset, index, dataType)

        # Storage.
        self.attributte = attribute
        self.preset = preset
        self.slotType = 'plug'

        # Methods.
        self._createStyle(parent)

    def _createStyle(self, parent):
        """
        Read the attribute style from the configuration file.

        """
        config = parent.scene().views()[0].config
        self.brush = QtGui.QBrush()
        self.brush.setStyle(QtCore.Qt.SolidPattern)
        self.brush.setColor(utils._convertDataToColor(config[self.preset]['plug']))

    def boundingRect(self):
        """
        The bounding rect based on the width and height variables.

        """
        width = height = int(self.parentItem().attrHeight / 2.0)

        nodzInst = self.scene().views()[0]
        config = nodzInst.config

        x = self.parentItem().baseWidth - int(width / 2.0)
        y = int(self.parentItem().baseHeight - config['node_radius'] +
             self.parentItem().attrHeight / 4 +
             self.parentItem().attrs.index(self.attribute) * self.parentItem().attrHeight)

        rect = QtCore.QRectF(QtCore.QRect(x, y, width, height))
        return rect

    def accepts(self, socket_item):
        """
        Only accepts socket items that belong to other nodes.

        """
        if isinstance(socket_item, SocketItem):
            if self.parentItem() != socket_item.parentItem():
                if self.dataType in socket_item.dataType or socket_item.dataType == "file" or self.dataType == "file":
                    if socket_item in self.connected_slots:
                        return False
                    else:
                        return True
            else:
                return False
        else:
            return False

    def connect(self, socket_item, connection):
        """
        Connect to the given socket_item.

        """
        # Populate connection.
        connection.socketItem = socket_item
        connection.plugNode = self.parentItem().nodeId
        connection.plugAttr = self.attribute

        # Add socket to connected slots.
        if socket_item in self.connected_slots:
            self.connected_slots.remove(socket_item)
        self.connected_slots.append(socket_item)

        # Add connection.
        if connection not in self.connections:
            self.connections.append(connection)

        # Emit signal.
        nodzInst = self.scene().views()[0]
        nodzInst.signal_PlugConnected.emit(connection.plugNode, connection.plugAttr, connection.socketNode, connection.socketAttr)

    def disconnect(self, connection):
        """
        Disconnect the given connection from this plug item.

        """
        # Emit signal.
        nodzInst = self.scene().views()[0]
        nodzInst.signal_PlugDisconnected.emit(connection.plugNode, connection.plugAttr, connection.socketNode, connection.socketAttr)

        # Remove connected socket from plug
        if connection.socketItem in self.connected_slots:
            self.connected_slots.remove(connection.socketItem)
        # Remove connection
        self.connections.remove(connection)
 

class SocketItem(SlotItem):

    """
    A graphics item representing an attribute in hook.

    """

    def __init__(self, parent, attribute, index, preset, dataType):
        """
        Initialize the socket.

        :param parent: The parent item of the slot.
        :type  parent: QtWidgets.QGraphicsItem instance.

        :param attribute: The attribute associated to the slot.
        :type  attribute: String.

        :param index: int.
        :type  index: The index of the attribute in the node.

        :type  preset: str.
        :param preset: The name of graphical preset in the config file.

        :param dataType: The data type associated to the attribute.
        :type  dataType: Type.

        """
        super(SocketItem, self).__init__(parent, attribute, preset, index, dataType)

        # Storage.
        self.attributte = attribute
        self.preset = preset
        self.slotType = 'socket'

        # Methods.
        self._createStyle(parent)

    def _createStyle(self, parent):
        """
        Read the attribute style from the configuration file.

        """
        config = parent.scene().views()[0].config
        self.brush = QtGui.QBrush()
        self.brush.setStyle(QtCore.Qt.SolidPattern)
        self.brush.setColor(utils._convertDataToColor(config[self.preset]['socket']))

    def boundingRect(self):
        """
        The bounding rect based on the width and height variables.

        """
        width = height = int(self.parentItem().attrHeight / 2.0)

        nodzInst = self.scene().views()[0]
        config = nodzInst.config

        x = - int(width / 2.0)
        y = int(self.parentItem().baseHeight - config['node_radius'] +
            (self.parentItem().attrHeight/4) +
             self.parentItem().attrs.index(self.attribute) * self.parentItem().attrHeight )

        rect = QtCore.QRectF(QtCore.QRect(x, y, width, height))
        return rect

    def accepts(self, plug_item):
        """
        Only accepts plug items that belong to other nodes.

        """
        if isinstance(plug_item, PlugItem):
            if (self.parentItem() != plug_item.parentItem() and
                len(self.connected_slots) <= 1):
                if plug_item.dataType in self.dataType or plug_item.dataType == "file" or self.dataType == "file":
                    if plug_item in self.connected_slots:
                        return False
                    else:
                        return True
            else:
                return False
        else:
            return False

    def connect(self, plug_item, connection):
        """
        Connect to the given plug item.

        """
        if len(self.connected_slots) > 0:
            # Already connected.
            self.connections[0]._remove()
            self.connected_slots = list()

        # Populate connection.
        connection.plugItem = plug_item
        connection.socketNode = self.parentItem().nodeId
        connection.socketAttr = self.attribute

        # Add plug to connected slots.
        self.connected_slots.append(plug_item)

        # Add connection.
        if connection not in self.connections:
            self.connections.append(connection)

        # Emit signal.
        nodzInst = self.scene().views()[0]
        nodzInst.signal_SocketConnected.emit(connection.plugNode, connection.plugAttr, connection.socketNode, connection.socketAttr)

    def disconnect(self, connection):
        """
        Disconnect the given connection from this socket item.

        """
        # Emit signal.
        nodzInst = self.scene().views()[0]
        nodzInst.signal_SocketDisconnected.emit(connection.plugNode, connection.plugAttr, connection.socketNode, connection.socketAttr)

        # Remove connected plugs
        if connection.plugItem in self.connected_slots:
            self.connected_slots.remove(connection.plugItem)
        # Remove connections
        self.connections.remove(connection)


class ConnectionItem(QtWidgets.QGraphicsPathItem):

    """
    A graphics path representing a connection between two attributes.

    """

    def __init__(self, source_point, target_point, source, target):
        """
        Initialize the class.

        :param sourcePoint: Source position of the connection.
        :type  sourcePoint: QPoint.

        :param targetPoint: Target position of the connection
        :type  targetPoint: QPoint.

        :param source: Source item (plug or socket).
        :type  source: class.

        :param target: Target item (plug or socket).
        :type  target: class.

        """
        super(ConnectionItem, self).__init__()

        self.setZValue(1)

        # Storage.
        self.socketNode = None
        self.socketAttr = None
        self.plugNode = None
        self.plugAttr = None

        self.source_point = source_point
        self.target_point = target_point
        self.source = source
        self.target = target

        self.plugItem = None
        self.socketItem = None

        self.movable_point = None

        self.data = tuple()

        # Methods.
        self._createStyle()

    def _createStyle(self):
        """
        Read the connection style from the configuration file.

        """
        config = self.source.scene().views()[0].config
        self.setAcceptHoverEvents(True)
        self.setZValue(-1)

        self._pen = QtGui.QPen(utils._convertDataToColor(config['connection_color']))
        self._pen.setWidth(config['connection_width'])

    def _outputConnectionData(self):
        """
        .

        """
        return ((self.plugNode, self.plugAttr),
                (self.socketNode, self.socketAttr))

    def mousePressEvent(self, event):
        """
        Snap the Connection to the mouse.

        """
        nodzInst = self.scene().views()[0]

        for item in nodzInst.scene().items():
            if isinstance(item, ConnectionItem):
                item.setZValue(0)

        nodzInst.drawingConnection = True

        d_to_target = (event.pos() - self.target_point).manhattanLength()
        d_to_source = (event.pos() - self.source_point).manhattanLength()
        if d_to_target < d_to_source:
            self.target_point = event.pos()
            self.movable_point = 'target_point'
            self.target.disconnect(self)
            self.target = None
            nodzInst.sourceSlot = self.source
        else:
            self.source_point = event.pos()
            self.movable_point = 'source_point'
            self.source.disconnect(self)
            self.source = None
            nodzInst.sourceSlot = self.target

        self.updatePath()

    def mouseMoveEvent(self, event):
        """
        Move the Connection with the mouse.

        """
        nodzInst = self.scene().views()[0]
        config = nodzInst.config

        mbb = utils._createPointerBoundingBox(pointerPos=event.scenePos().toPoint(),
                                              bbSize=config['mouse_bounding_box'])

        # Get nodes in pointer's bounding box.
        targets = self.scene().items(mbb)

        if any(isinstance(target, NodeItem) for target in targets):

            if nodzInst.sourceSlot.parentItem() not in targets:
                for target in targets:
                    if isinstance(target, NodeItem):
                        nodzInst.currentHoveredNode = target
        else:
            nodzInst.currentHoveredNode = None

        if self.movable_point == 'target_point':
            self.target_point = event.pos()
        else:
            self.source_point = event.pos()

        self.updatePath()

    def mouseReleaseEvent(self, event):
        """
        Create a Connection if possible, otherwise delete it.

        """
        nodzInst = self.scene().views()[0]
        nodzInst.drawingConnection = False

        slot = self.scene().itemAt(event.scenePos().toPoint(), QtGui.QTransform())

        if not isinstance(slot, SlotItem):
            self._remove()
            self.updatePath()
            super(ConnectionItem, self).mouseReleaseEvent(event)
            return

        if self.movable_point == 'target_point':
            if slot.accepts(self.source):
                # Plug reconnection.
                self.target = slot
                self.target_point = slot.center()
                plug = self.source
                socket = self.target

                # Reconnect.
                socket.connect(plug, self)

                self.updatePath()
            else:
                self._remove()

        else:
            if slot.accepts(self.target):
                # Socket Reconnection
                self.source = slot
                self.source_point = slot.center()
                socket = self.target
                plug = self.source

                # Reconnect.
                plug.connect(socket, self)

                self.updatePath()
            else:
                self._remove()

    def _remove(self):
        """
        Remove this Connection from the scene.

        """
        if self.source is not None:
            self.source.disconnect(self)
        if self.target is not None:
            self.target.disconnect(self)

        scene = self.scene()
        scene.removeItem(self)
        scene.update()

    def updatePath(self):
        """
        Update the path.

        """
        self.setPen(self._pen)

        path = QtGui.QPainterPath()
        path.moveTo(self.source_point)
        dx = (self.target_point.x() - self.source_point.x()) 
        dy = self.target_point.y() - self.source_point.y()

        ctrl1 = QtCore.QPointF(self.source_point.x() + dx * 0.5, self.source_point.y() + dy * 0)
        ctrl2 = QtCore.QPointF(self.source_point.x() + dx * 0.5, self.source_point.y() + dy * 1)
        path.cubicTo(ctrl1, ctrl2, self.target_point)
        self.setPath(path)