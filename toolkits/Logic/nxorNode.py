from wario import Node

class nxorNode(Node):

    def __init__(self, name, params):   
        super(nxorNode, self).__init__(name, params)
        
    def process(self):
        b1 = ~ self.args["In 1"]
        b2 = ~ self.args["In 2"]
        
        out = b1 ^ b2
        return {"Out" : out}