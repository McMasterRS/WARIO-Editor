from wario import Node

class intSubtractor(Node):

    def __init__(self, name):
        super(intSubtractor, self).__init__(name)

    def process(self, inA, inB):
        return inA-inB