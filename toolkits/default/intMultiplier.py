from pipeline.Node import Node

class intMultiplier(Node):    

    def __init__(self, name):
        super(intMultiplier, self).__init__(name)
        
    # def process(self, inA, inB):
    def process(self):
        return {"Out": self.state['In A'] * self.state['In B']}