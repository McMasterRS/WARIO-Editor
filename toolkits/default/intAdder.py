from pipeline.Node import Node

class intAdder(Node):
    def __init__(self, name):
        super(intAdder, self).__init__(name)

    def process(self):
        return {"Out": self.args['In A'] + self.args['In B']}