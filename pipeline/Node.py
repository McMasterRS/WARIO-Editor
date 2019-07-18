from pipeline.NodeFactory import NodeFactory
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog
from PyQt5.QtGui import QIcon
import csv
###################################################################################################
# Node/Task
# + Abstract node for handling the running of a discrete task in a workflow
###################################################################################################

class Node():
    """ Abstract Node class. This describes a single operational function in our process pipeline """

    ################################################################################################
    # Node.__init__: Initializes the node
    # + node_id: The unique id for the node.
    ################################################################################################
    def __init__(self, node_id=None):
        """ Initialize Node """
        self.node_id = node_id  # identifier for the node
        self.ready = {}         # Flags for each argument, all true indicates the node should run
        self.state = {}         # Variables local to the node, set internally by itself. Persits
        self.args = {}          # Variables local to the node, set externally by it's parents
        self.global_vars = {}   # Variables global to the entire pipeline.
        self.done = True        # Flag indicating if this node requires multple passes
        self.event_callbacks = {}
        self.events_fired = {}

    ################################################################################################
    # Node.start: Pipeline runs this when the pipeline starts
    ################################################################################################
    def start(self):
        """ Default start hook ran by the pipeline before all processing begins """
        return None
        
    ################################################################################################
    # Node.start: Pipeline runs this when the node is ready
    ################################################################################################
    def process(self):
        """ Default process hook ran by the pipeline when this node is ready """
        return {}

    ################################################################################################
    # Node.reset: Pipeline runs this to reset this nodes state variables
    ################################################################################################    
    def reset(self):
        """ Default process hook ran by the pipeline to reset this node's state variables """
        return None
        
    ################################################################################################
    # Node.end: Pipeline runs this when the pipeline ends
    ################################################################################################    
    def end(self):
        """ Default end hook ran by the pipeline once the pipeline has finished """
        return None

    ################################################################################################
    # TODO: This can more intelligently be completed at each adding of data from upstream
    ################################################################################################
    def is_ready(self):
        ready = True
        for param in self.ready:
            ready = ready and param in self.state
        print(self, self.state, self.ready, ready)
        return ready

class CSVOutputGUINode(Node):
    def __init__(self, name):
        super().__init__(name)
        self.state['csv_out'] = [[]]
        self.state['current_row'] = self.state['csv_out'][0]
        self.event_callbacks = {
            "Row End": self.on_row_end
        }

    def process(self):
        self.state['current_row'].append(self.args['IN'])

    def end(self):
        app = QApplication(sys.argv)
        ex = FileWidget()
        print(self.state['csv_out'])
        file = ex.saveFileDialog()
        if file != '':
            with open(file, 'w') as f:
                writer = csv.writer(f)
                while len(self.state['csv_out']) > 0:
                    row = self.state['csv_out'].pop()
                # for row in self.state['csv_out']:
                    writer.writerow(row)


    def on_row_end(self, event_id, event_data):
        print("####################################### Row End Heared")
        current_row = []
        self.state['csv_out'].append(current_row) # create a new row for the output
        self.state['current_row'] = current_row

class CSVInputGUINode(Node):
    def __init__(self, name):
        super().__init__(name)
        self.done = False
        self.state['batch'] = [] 
        self.state['run'] = [] 
        self.state['row'] = []

    def start(self):
        app = QApplication(sys.argv)
        ex = FileWidget()
        self.state['files'] = ex.openFileNamesDialog()
        self.state['batch'] = []
        for file_path in self.state['files']:
            with open(file_path) as csv_file:
                reader = csv.reader(csv_file)
                data = []
                for row in reader:
                    data.append(row)
                self.state['batch'].append(data)

    def process(self):
        print("##### Process #####")
        item = None

        if len(self.state['row']) > 0:
            item = self.state['row'].pop()

        elif len(self.state['run']) > 0:
            self.state['row'] = self.state['run'].pop()
            item = self.state['row'].pop()
            self.events_fired["Row End"] = None

        elif len(self.state['batch']) > 0:
            self.state['run'] = self.state['batch'].pop()
            self.state['row'] = self.state['run'].pop()
            item = self.state['row'].pop()
            self.events_fired["Run End"] = ("Run End", None)

        if len(self.state["batch"]) == 0 and len(self.state["run"]) == 0 and len(self.state["row"]) == 0:
            self.done = True
            self.events_fired["Batch End"] = ("Batch End", None)

        return {
            "OUT": item
        }

class TestNode(Node):
    def process(self):
        print(self.args['IN'])
        return {}

class FileWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Select Some Files'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
    
    def openFileNamesDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","All Files (*);;Python Files (*.py)", options=options)
        self.show()
        return files
    
    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;Text Files (*.txt)", options=options)
        self.show()
        return fileName
