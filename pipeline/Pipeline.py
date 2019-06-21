class Pipeline():
    
    """
    proccess flow pipeline. Oversees/orchestrates the running of a directed graph of arbitrary function nodes
    
    """

    def __init__(self, nodes=None):
        
        """
        initializes a pipeline, optionally with a set of nodes
        
        """

        self.nodes = nodes
        self.pipes = {} # each connection, indexed by parent node. Pipes are always between two nodes
        self.roots = []
        self.leaves = []
        self.longest_path = 0
        self.shortest_path = 0

    def add_node(self, node, children=None, parents=None):
        
        """
        add a single node
        
        """

        self.nodes[node.name] = node

        # TODO: check if this is iteratible
        for child in children:
            self.connect(node, child)

        for parent in parents:
            self.connect(parent, node)


    def connect(self, parent, child):

        # if the parent isn't already in the pipeline somewhere, add it in.
        if parent.name not in self.nodes:
            self.add_node(parent, children=[child])

        # if the parent was a leaf node, remove it.
        elif parent.name in self.leaves:
            self.leaves.pop(parent.name)

        # if the child isn't in the pipeline, add it in.
        if child.name not in self.nodes:
            self.add_node(child, parents=[parent])

        # if the child was a root node, remove it.
        elif child.name in self.roots:
            self.roots.pop(child.name)


    def node_beginning(self, node):
        pass

    def node_running(self, node):
        pass

    def node_ending(self, node):
        pass