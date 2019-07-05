import json

###################################################################################################
#
###################################################################################################

class Pipeline():
    """  Proccess flow pipeline. Oversees/orchestrates the running of a directed graph of arbitrary tasks  """

    nodes = {}          # All of the functional nodes
    edges = {}          # The connective relationships between each node
    data = {}           # The data before it is consumed by a node in processing, this is filled each time a node is tried to run
    roots = {}          # Nodes with no parents. Updated as needed when new tasks are added, reduces need to search the whole graph

    delayed_nodes = {
        'batch': [],
        'run': [],
        'row': [] 
    }

    def add(self, node, node_id, delay=False):
        self.nodes[node_id] = node
        self.edges[node_id] = {
            'outgoing': {},
            'incoming': {}
        }
        self.data[node_id] = {}
        if delay:
            print(delay, node_id)
            self.delayed_nodes[delay].append(node_id)

    def delete(self, ID):
        self.nodes[ID].delete()

    def connect(self, parent_id, child_id, parent_attribute, child_attribute):

        print("CONNECT", parent_id, child_id, parent_attribute, child_attribute)

        # parts out the different data types into easier to work with names
        parent_edges = self.edges[parent_id]['outgoing']
        child_edges = self.edges[child_id]['incoming']
        child_data = self.data[child_id]

        # if this attribute hasnt already been accessed we may have to initialize it
        if child_attribute not in child_data:
            child_data[child_attribute] = None

        # the attribute on which the two nodes are connecting on may or may not already have been initialized by another connection
        if parent_attribute not in parent_edges:
            parent_edges[parent_attribute] = []
        if child_attribute not in child_edges:
            child_edges[child_attribute] = []

        # store the relationship on that respective edge for both the parent and child so they can look eachother up later
        parent_edges[parent_attribute].append([child_id, child_attribute])
        child_edges[child_attribute].append([parent_id, parent_attribute])

        return parent_edges, child_edges

    def flow(self, parent_id, parent_attribute, data):

        # parts out the different data types into easier to work with names
        parent_edges = self.edges[parent_id]['outgoing']
        parent_edge = parent_edges[parent_attribute]

        for outgoing in parent_edge: # this might be better called terminals and edges
            child_id, child_attribute = outgoing
            child_data = self.data[child_id]
            # stores the data in the appropriate attribute location of the child
            child_data[child_attribute] = data
            print("FLOW from [ ", parent_id, "] on [", parent_attribute, "] to [", child_id, "] on [", child_attribute, "] send [", child_data, "]")

        return child_data

    def process_input(self, node_id, visited):
        # Parts out the different data types into easier to work with variables
        node = self.nodes[node_id]                          # the node we want to run
        outgoing = self.edges[node_id]['outgoing']          # the outgoing connections, one terminal can connect to multiple children

        batch = node.load_batch() # this is an extremely confusing use of this

        for run in batch:
            for row in run:
                for item in row:
                    self.process_node(node_id, {}, item)
                    print("--------------------------------------- DONE ROW ---------------------------------------")
                    self.process_delayed("row")
            print("--------------------------------------- DONE RUN ---------------------------------------")
            self.process_delayed("run")
        print("--------------------------------------- DONE BATCH ---------------------------------------")
        self.process_delayed("batch")
        
        
    def process_node(self, node_id, visited, *args, **kwargs):

        # Parts out the different data types into easier to work with variables
        node = self.nodes[node_id]                          # the node we want to run
        outgoing = self.edges[node_id]['outgoing']          # the outgoing connections, one terminal can connect to multiple children
        data = self.data[node_id]                           # the data that the node will run on

        if node_id not in self.delayed_nodes['batch'] and node_id not in self.delayed_nodes['run'] and node_id not in self.delayed_nodes['row']:
            print("RUNNING: ", node_id)
            visited[node_id] = True # passed recursively when visiting the nodes. we only want to run nodes once, unless there is a batch.

            results = node._process(*data) # processes the node
            print("PROCESS RESULTS: ", node_id, results)

            # we want to child nodes to have acces to the results of this node/task, we do this by 'flowing' it down
            for outgoing_terminal in results:
                if outgoing_terminal in outgoing:
                    self.flow(node_id, outgoing_terminal, results[outgoing_terminal])

            # Next we want to run all of the child nodes that connect to this node through its outgoing terminals
            for edges in outgoing:
                for edge in outgoing[edges]:
                    child_id = edge[0]
                    if child_id not in visited:
                        self.process_node(child_id, visited)

        return node_id

    def process_delayed(self, delay_id):
        if delay_id in self.delayed_nodes:
            length = range(len(self.delayed_nodes[delay_id]))
            print(delay_id, " delayed: ", self.delayed_nodes[delay_id])
            for i in length:
                node = self.delayed_nodes[delay_id].pop()
                print("============================", node)
                self.process_node(node, {})
                print("============================", node)
