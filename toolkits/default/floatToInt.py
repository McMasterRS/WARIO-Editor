from wario import Node

class floatToInt(Node):

    def __init__(self, name):
        super(floatToInt, self).__init__(name)
        
    def process(self, floatIn):
        return {int(floatIn)}