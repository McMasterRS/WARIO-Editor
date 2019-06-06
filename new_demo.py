from Qt import QtCore, QtWidgets
import nodz_main

try:
    app = QtWidgets.QApplication([])
except:
    # I guess we're running somewhere that already has a QApp created
    app = None

nodz = nodz_main.Nodz(None)
# nodz.loadConfig(filePath='')
nodz.initialize()
nodz.show()
#nodz.gridVisToggle = False

######################################################################
# Test signals
######################################################################

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

# Node A
nodeA = nodz.createNode(name='Source A', preset='node_preset_1', position=None)

nodz.createAttribute(node=nodeA, name='Integer', index=-1, preset='attr_preset_1',
                     plug=True, socket=False, dataType=int)



# Node B
nodeB = nodz.createNode(name='Source B', preset='node_preset_1')

nodz.createAttribute(node=nodeB, name='Integer', index=-1, preset='attr_preset_1',
                     plug=True, socket=False, dataType=int)





# Node C
nodeC = nodz.createNode(name='Adder', preset='node_preset_1')

nodz.createAttribute(node=nodeC, name='Integer A', index=-1, preset='attr_preset_1',
                     plug=False, socket=True, dataType=int)

nodz.createAttribute(node=nodeC, name='Integer B', index=-1, preset='attr_preset_1',
                     plug=False, socket=True, dataType=int)

nodz.createAttribute(node=nodeC, name='Sum', index=-1, preset='attr_preset_1',
                     plug=True, socket=False, dataType=int)

nodeD = nodz.createNode(name='Output', preset='node_preset_1')

nodz.createAttribute(node=nodeD, name='Integer', index=-1, preset='attr_preset_1',
                     plug=False, socket=True, dataType=int)


if app:
    # command line stand alone test... run our own event loop
    app.exec_()
