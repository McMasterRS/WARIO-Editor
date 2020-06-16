import csv
from pipeline.Node import Node
from pipeline.FileWidget import FileWidget
from PyQt5.QtWidgets import QApplication

class CSVInputGUINode(Node):

    def __init__(self, name):
        super().__init__(name)
        self.done = False
        self.state['batch'] = [] 
        self.state['run'] = [] 
        self.state['row'] = []

    def start(self):
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