from pipeline.Node import Node

class notNode(Node):

    def __init__(self, name, params):   
        super(notNode, self).__init__(name, params)
        
    def process(self):

        out = not self.args["In"]
        return {"Out" : out}