from PyQt5 import QtWidgets, uic
from blinker import signal
import os


class LoopData():
    def __init__(self):
        self.start = {}
        self.end = {}
        self.nodes = []
        self.name = ""
        self.type = {}

    def addNode(self, node):
        if self.nodes.count(node) == 0:
            self.nodes.append(node)
        


class LoopBuilder(QtWidgets.QWidget):
    def __init__(self, parent):
        super(LoopBuilder, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'LoopBuilder.ui'), self)
        self.show()

        self.parent = parent
        self.currentData = LoopData()
        self.data = []

        # Connect buttons
        self.btStart.clicked.connect(self.setStart)
        self.btEnd.clicked.connect(self.setEnd)
        self.btAdd.clicked.connect(self.addNodes)
        self.btDetect.clicked.connect(self.detectNodes)
        self.btReset.clicked.connect(self.resetNodes)
        self.cbLoopType.currentIndexChanged.connect(self.changeType)
        self.btCreate.clicked.connect(self.createLoop)
        self.btEdit.clicked.connect(self.editLoop)

        self.swLoopType.setCurrentIndex(0)

    # Set the start node for the current loop
    def setStart(self):
        items = self.parent.scene().selectedItems()
        if len(items) == 1:
            node = items[0]
            self.currentData.start = {"name" : node.name, "ID" : node.nodeId}
            self.lbStart.setText(node.name)
        elif len(items) == 0:
            QtWidgets.QMessageBox.critical(self, "Error", "No node selected in pipeline interface")
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "Only one node can be set as the start node")
        
    # Set the end node for the current loop
    def setEnd(self):
        items = self.parent.scene().selectedItems()
        if len(items) == 1:
            node = items[0]
            self.currentData.end = {"name" : node.name, "ID" : node.nodeId}
            self.lbEnd.setText(node.name)
        elif len(items) == 0:
            QtWidgets.QMessageBox.critical(self, "Error", "No node selected in pipeline interface")
        else:
            QtWidgets.QMessageBox.critical(self, "Error", "Only one node can be set as the end node")

    # Adds all selected nodes to loop
    def addNodes(self):
        items = self.parent.scene().selectedItems()
        if len(items) == 0:
            QtWidgets.QMessageBox.critical(self, "Error", "No nodes selected in pipeline interface")
        for node in self.parent.scene().selectedItems():
            self.currentData.addNode(node.nodeId)
    
    # Detects which nodes to add by walking connections
    def detectNodes(self):
        pass

    # Resets the loop's nodes
    def resetNodes(self):
        self.currentData.start = {}
        self.currentData.end = {}
        self.currentData.nodes = []

    # Changes the type panel to match the combobox
    def changeType(self, index):
        self.swLoopType.setCurrentIndex(index)

    # Creates a new loop and inserts it into the table
    def createLoop(self):

        rowPos = self.tbLoops.rowCount()

        # Override existing loop if it shares the same name
        for data, i in enumerate(self.data):
            if data.name == self.tbName.text():
                rowPos = i
                break
        # Create new row if no matching loop found
        else:
            self.tbLoops.insertRow(rowPos)

        # Populate the table
        self.tbLoops.setItem(rowPos, 0, QtWidgets.QTableWidgetItem(self.currentData.name))
        self.tbLoops.setItem(rowPos, 1, QtWidgets.QTableWidgetItem(self.currentData.start["name"]))
        self.tbLoops.setItem(rowPos, 2, QtWidgets.QTableWidgetItem(self.currentData.end["name"]))

        # Last column is based on the selected break type
        if (self.cbLoopType.currentIndex() == 0):
            self.currentData.type = {"type" : "iter", "var" : self.sbCount.value()}
            self.tbLoops.setItem(rowPos, 3, QtWidgets.QTableWidgetItem("Iteration Count (" + str(self.sbCount.value()) + ")"))
        elif (self.cbLoopType.currentIndex() == 1):
            self.currentData.type = {"type" : "custom", "var" : self.tbSignalName.text()}
            self.tbLoops.setItem(rowPos, 3, QtWidgets.QTableWidgetItem("Custom Signal (" + self.tbSignalName.text() + ")"))

        # Populate the rest of the data object
        self.currentData.name = self.tbName.text()

        # Add to data list and reset current data
        self.data.append(self.currentData)
        self.currentData = LoopData()

        # Clean UI fields
        self.tbName.setText("")
        self.lbStart.setText("")
        self.lbEnd.setText("")
        self.sbCount.setValue(1)
        self.tbSignalName.setText("")
        self.btCreate.setText("Create Loop")

    def editLoop(self):
        row = self.tbLoops.currentRow()
        if row == -1:
            return
        
        # Move the data from that row's object into the UI
        self.tbName.setText(self.data[row].name)
        self.lbStart.setText(self.data[row].start["name"])
        self.lbEnd.setText(self.data[row].end["name"])
        if self.data[row].type["type"] == "iter":
            self.sbCount.setValue(self.data[row].type["var"])
            self.cbLoopType.setCurrentIndex(0)
            self.changeType(0)
        elif self.data[row].type["type"] == "custom":
            self.tbSignalName.setText(self.data[row].type["var"])
            self.cbLoopType.setCurrentIndex(1)
            self.changeType(1)

        self.currentData = self.data[row]
        self.btCreate.setText("Save changes")

    def deleteLoop(self):
        row = self.tbLoops.currentRow()
        if row == -1:
            return

        msg = QtWidgets.QMessageBox.warning(self, "Warning", "Are you sure you want to delete this loop?")
        msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if msg == QtWidgets.QMessageBox.Yes:
            self.tbLoops.removeRow(row)
            self.data.pop(row)