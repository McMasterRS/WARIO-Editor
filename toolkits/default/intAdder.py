from wario import Node

class intAdder(Node):
    def __init__(self, name, params):
        super(intAdder, self).__init__(name, params)

    def process(self):
        return {"Out": self.args['In A'] + self.args['In B']}