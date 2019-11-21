import csv
from pipeline.Node import Node
from pipeline.FileWidget import FileWidget

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
