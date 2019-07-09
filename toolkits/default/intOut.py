from pipeline.Node import Node

class intOut(Node):

    def __init__(self, name):
        super(intOut, self).__init__(name)

    def process(self):
        print("Float: ", self.state["In"])
        return self.state["In"]