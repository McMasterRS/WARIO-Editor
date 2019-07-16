from pipeline.Node import Node
import random

class randomInt(Node):

    def __init__(self, name):
        super(randomInt, self).__init__(name)
        
    def process(self):
        return {
            "Out": int(random.randrange(self.args["min"], self.args["max"]))
        }