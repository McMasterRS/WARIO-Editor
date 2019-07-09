from pipeline.Node import Node

class intDividerF(Node):

    def __init__(self, name):
        super(intDividerF, self).__init__(name)
        
    def process(self, inA, inB):
        return inA/inB