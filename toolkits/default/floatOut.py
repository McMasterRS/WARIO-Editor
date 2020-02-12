from wario import Node

class floatOut(Node):

    def __init__(self, name):
        super(floatOut, self).__init__(name)
        
    def process(self, floatIn):
        print("Float: ", floatIn)
        return floatIn