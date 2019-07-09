from pipeline.Node import Node

class floatToInteger(Node):

    def __init__(self, name):
        super(floatToInteger, self).__init__(name)
        
    def process(self, floatIn):
        return {int(floatIn)}