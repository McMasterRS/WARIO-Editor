import json
from PyQt5 import QtWidgets

class TreeItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, parent, name, file):
        super(TreeItem, self).__init__(parent, name)
        self.file = file

# Walks through the nodes in a pipeline starting from the root and generates tree widgets based on these.
# This allows for developers to create custom UIs that display information for each node post-run while
# preserving the order that each node is run
class WalkTree():
    def __init__(self, data):
    
        self.nodes = {}
        self.connections = []
        self.tree = {}
        self.maxDepth = 0
        
        with open(data, 'r') as f:
            # load data
            data = json.load(f) 
            if "NODES" in data:
                nodeKeys = list(data["NODES"].keys())
                for key in nodeKeys:
                    self.nodes[key] = data["NODES"][key]["name"]
                
            
            # trim attribute names off connections
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
        
        # Walk tree from each root
        for root in roots:
            self.walkTree(root, None, 0)
                    
    # Walk the tree
    def walkTree(self, node, parent, depth):
        # Assigns a parent and depth to each node, updating if a higher depth is found
        if node not in self.tree.keys() or self.tree[node]["depth"] < depth:
            self.tree[node] = {"parent" : parent, "depth" : depth}
            
        # Loops through all connections for that node and walks them
        for con in self.connections:
            if con[0] == node:
                if depth + 1 > self.maxDepth:
                    self.maxDepth = depth + 1
                self.walkTree(con[1], node, depth + 1)
                
    # builds the tree widget items based on the walked tree
    def buildWidget(self, root = None):
        itemList = {}
        for i in range(0, self.maxDepth+1):
            for node in self.tree:
                if self.tree[node]["depth"] == i:
                
                    if i == 0:
                        parent = root
                    else:
                        parent = itemList[self.tree[node]["parent"]]
                        
                    itemList[node] = TreeItem(parent, [self.nodes[node]], None)
                    
        return itemList