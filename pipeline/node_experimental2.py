class Node():
    def __init__(self, fn, incoming=None, outgoing=None):
        self.model = NodeModel()
        self.view = NodeView()
    
        self.model.incoming = incoming
        self.model.outgoing = outgoing

    def run():

class NodeView():
    pass

class NodeController():
    pass

class NodeModel():
    pass