from pipeline.Node import Node

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

    # TODO: Validation step for initialization arguments
    def __init__(self, nodes=None, global_vars=None, roots=None):
        """ Pipeline initialization. Optionally can initialize with nodes, global_vars, roots """
        # tree of nodes, each node stores its return attributes which in turn stores its children
        self.nodes = nodes if nodes is not None else {}
        # Nodes with no parents. Updated as needed when new tasks are added, reduces need to search the whole graph
        self.roots = roots if roots is not None else {}
        # Variables that are optionally shared accross nodes and batches/runs/passes
        self.global_vars = global_vars if global_vars is not None else {}

    ################################################################################################
    # Pipeline: Add
    # + node: the node that will be added to the pipeline
    ################################################################################################
    def add(self, node):
        """ Add a new node to the pipeline """

        self.nodes[node] = {}
        self.roots[node] = node

    ################################################################################################
    # Pipeline: Connect
    # + parent: the node that will be upstream from the child
    # + child: the node that will be downstream from the parent
    # + parent_terminal: On what outgoing parameter is the parent node connecting
    # + child_terminal: On what incoming parameter is the child node connecting
    ################################################################################################
    def connect(self, parent=None, child=None):
        """ Form a relationship between two nodes, from the parent data will be passed to child """
 
        parent_node, parent_terminal = parent
        child_node, child_terminal = child
        child_node.ready[child_terminal] = False
        if parent_terminal not in self.nodes[parent_node]:
            self.nodes[parent_node][parent_terminal] = []
        self.nodes[parent_node][parent_terminal].append([child_node, child_terminal])

    ###############################################################################################
    # Pipeline: Start:
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
    # Pipeline: Run_Pass
    # + done: Indicates if more passes over the data need to be done
    #
    ### Recursively run passes over the pipeline until each node has processed all of its data.
    ### Since a pipeline can have input nodes that iteratively return parts of their data (batches)
    ### multiple runnings of these nodes must be performed (a pass). Each pass over the data runs
    ### all of the nodes from the start until they all report that they are done.
    ###############################################################################################

    def run_pass(self, done):
        """ Recursively runs all of the roots nodes until they report they are done """

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
        """ Called on each node, and recursively on each child node """

        print("Node", node, "State", node.state, "Ready", node.ready, all(node.ready.values()))
        if all(node.ready.values()):

            node.global_vars = self.global_vars
            results = node.process()
            self.global_vars = node.global_vars

            for terminal in self.nodes[node]:
                for child, child_terminal in self.nodes[node][terminal]:

                    child.args[child_terminal] = results[terminal]
                    child.ready[child_terminal] = True
                    if child not in visited:
                        self.run_node(child, visited)

        return node.done