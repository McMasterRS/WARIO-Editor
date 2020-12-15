from wario import Node

class intToFloat(Node):

    def __init__(self, name):
        super(intToFloat, self).__init__(name)
        
    def process(self, intIn):
        return {"Out": float(intIn)}