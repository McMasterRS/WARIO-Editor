from wario import Node
import random

class randomInt(Node):

    def __init__(self, name, params):
        super(randomInt, self).__init__(name, params)
        
    def process(self):
        return {
            "Out": int(random.randrange(self.args["min"], self.args["max"]))
        }