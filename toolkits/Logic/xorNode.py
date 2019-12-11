from pipeline.Node import Node

class xorNode(Node):

    def __init__(self, name, params):   
        super(xorNode, self).__init__(name, params)
        
    def process(self):
        b1 = self.args["In 1"]
        b2 = self.args["In 2"]
        
        out = b1 ^ b2
        return {"Out" : out}