from pipeline.Node import Node

import csv

class importCSV(Node):

    def __init__(self, params):
        self.data = csv.reader(params["filename"], 'rb')
        self.current = []
        self.currentIndex = 0
        self.type = params["type"]

    def run(self):
    
        if self.type == "row":
            return {"Data" : self.data.next()}
        elif self.type == "item":
            if self.currentIndex > len(self.current) - 1:
                self.current = self.data.next()
                self.currentIndex = 0
            
            return {"Data" : self.current[self.currentIndex]}