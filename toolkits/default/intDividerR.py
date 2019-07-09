from pipeline.Node import Node

class intDividerR(Node):

    def __init__(self, name):
        super(intDividerR, self).__init__(name)
        
    def process(self, inA, inB):
        return inA/inB