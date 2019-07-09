import json

###################################################################################################
# Pipeline:
#
### The main process pipeline. Responsible for orchestrating a sequence of discrete tasks, as can
### be defined as an acyclic directed graph. Each node runs a singular operation then passes/flows
### it's results downstream onto the next. Data is collected within the node's themselves until all
### it's parents upstream have finished their own respective tasks. Some nodes can produce subsets
### of their own data, indicating that all nodes downstream from it should be run that many more
### times.
###################################################################################################

class Pipeline():
    """  Proccess flow pipeline. Oversees/orchestrates the running of a directed graph of arbitrary tasks  """

    nodes = {}          # tree of nodes, each node stores its return attributes which in turn stores its children
    roots = {}          # Nodes with no parents. Updated as needed when new tasks are added, reduces need to search the whole graph

    ################################################################################################
    # Pipeline: Add
    # + node: the node that will be added to the pipeline
    ################################################################################################
    def add(self, node):
        """ Add a new node to the pipeline """
        self.roots[node] = node
        self.nodes[node] = {}

    ################################################################################################
    # Pipeline: Connect
    # + parent: the node that will be upstream from the child
    # + child: the node that will be downstream from the parent
    # + parent_terminal: On what outgoing parameter is the parent node connecting
    # + child_terminal: On what incoming parameter is the child node connecting
    ################################################################################################
    def connect(self, parent, child, parent_terminal, child_terminal):
        """ Form a relationship between two nodes, from the parent data will be passed to child """

        print("CONNECT", parent, child, parent_terminal, child_terminal)

        if parent_terminal not in self.nodes[parent]:
            self.nodes[parent][parent_terminal] = []
        
        self.nodes[parent][parent_terminal].append([child, child_terminal])

    ###############################################################################################
    # Pipeline.Start: Initiates the pipeline
    ###############################################################################################
    def start(self):
        """ Initializes all the nodes and starts the first pass """
        print(self.nodes)

        print("############################ Starting ############################")

        # runs each node's start function once at the beginning
        for node in self.nodes:
            node.start()

        if len(self.roots) > 0:
            self.run_pass(True)

    ###############################################################################################
    # Pipeline.run_pass: Recursively run passes of the pipeline until all data is processed
    # + done: indicates if more passes over the data need to be done
    ### Since a pipeline can have input nodes that iteratively return parts of their data, multiple
    ### runnings of these nodes must be performed. Each pass over the data runs all of the nodes
    ### from the start until they all report that they have processed all of their available data
    ###############################################################################################

    def run_pass(self, done):
        """ Recursively runs all of the roots nodes until they report they are done """
        print("Pass ###")

        for root in self.roots:
            done = done and self.run_node(root, {})

        if not done:
            self.run_pass(True)


    ################################################################################################
    # Pipeline: Process Node
    # + node_id: Unique identifier for retrieving the node to be processed
    # + visited: Dictionary of already visited nodes, recursively filled as the graph is traversed
    #
    ### Recursive function to traverse the sequence of nodes (the graph) visiting each node once and
    ### running it's accompanied process function. Data for running each node is retrieved from that
    ### node's upstream buffer and passed in as simple arguments.
    ################################################################################################

    def run_node(self, node, visited):
        """ called on each node, and recursively on each child node """
        print(node.state)
        if node.is_ready():
            visited[node] = True

            # results = node.process(*node.state.values()) # processes the node and retrieves the results
            results = node.process()
            # print(node, 'results', results)
            for terminal in self.nodes[node]:
                for child, child_terminal in self.nodes[node][terminal]:
                    print(child_terminal, results[terminal])
                    child.state[child_terminal] = results[terminal]
                    child.ready[child_terminal] = True
                    if child not in visited:
                        # print("child", child)
                        self.run_node(child, visited)

        return node.done