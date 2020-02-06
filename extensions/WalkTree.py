import json

class WalkTree():
    def __init__(self, data):
    
        self.nodes = []
        self.connections = []
        self.tree = {}
        
        with open(data, 'r') as f:
            # load data
            data = json.load(f) 
            if "NODES" in data:
                self.nodes = list(data["NODES"].keys())
            
            # trims attribute names off connections
            if "CONNECTIONS" in data:
                self.connections = [[c.split(".")[0] for c in conn] for conn in data["CONNECTIONS"]]

        # Find roots
        roots = []
        for node in self.nodes:
            root = True
            for con in self.connections:
                if con[1] == node:
                    root = False
            
            if root == True:
                roots.append(node)
        
        for root in roots:
            self.walkTree(root, None, 0)
                    
    def walkTree(self, node, parent, depth):
        if node not in self.tree.keys() or self.tree[node]["depth"] < depth:
            self.tree[node] = {"parent" : parent, "depth" : depth}
            
        for con in self.connections:
            if con[0] == node:
                self.walkTree(con[1], node, depth + 1)