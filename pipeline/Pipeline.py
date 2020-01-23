from pipeline.Node import Node
from pipeline.SignalHandler import SignalHandler

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
        # tree of nodes, storing return value names and its subsequent children
        self.nodes = nodes if nodes is not None else {}
        # Nodes with no parents. Updated as needed when new tasks are added, reduces need to search the whole graph
        self.roots = roots if roots is not None else {}
        # Variables that are optionally shared accross nodes and batches/runs/passes
        self.global_vars = global_vars if global_vars is not None else {}
        # Signals
        self.signals = SignalHandler()
        # 
        self.event_callbacks = {}
        #
        self.results = {}
        # Enable debug prints
        self.verbose = False

    ################################################################################################
    # Pipeline: Add
    # + node: the node that will be added to the pipeline
    ################################################################################################
    def add(self, node):
        """ Add a new node to the pipeline """

        self.nodes[node] = []   
        self.roots[node] = node
        if len(node.event_callbacks) > 0:
            print(node.event_callbacks)
            for event_id in node.event_callbacks:
                event_callback = node.event_callbacks[event_id]
                if event_id not in self.event_callbacks:
                    self.event_callbacks[event_id] = []
                self.event_callbacks[event_id].append(event_callback)

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
        child_node.default_ready[child_terminal] = False

        if parent_node not in self.nodes:
            self.nodes[parent_node] = []

        # if parent_terminal not in self.nodes[parent_node]:
        #     self.nodes[parent_node][parent_terminal] = []

        # self.nodes[parent_node][parent_terminal].append([child_node, child_terminal])
        self.nodes[parent_node].append((parent_terminal, child_terminal, child_node))

        if child_node in self.roots:
            self.roots.pop(child_node)

        return self.nodes[parent_node][-1]

    ###############################################################################################
    # Pipeline: Start:
    ###############################################################################################
    def start(self):
        """ Initializes all the nodes and starts the first pass """
        if self.verbose:
            print(self.nodes)

        print("############################ Starting ############################")

        # runs each node's start function once at the beginning
        for node in self.nodes:
            node.start()

        if len(self.roots) > 0:
            results = False
            while results == False:
                self.signals.start.send(self)
                results = self.run_pass(True)
        
        for node in self.nodes:
            node.end()

        self.signals.end.send(self)
        print("############################ Finishing ############################")
        
        return results

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
            results, _done = self.run_node(root, {})
            done = done and _done

        if not done:
            return False

        return True

    ################################################################################################
    # Pipeline: Process Node
    # + node_id: Unique identifier for retrieving the node to be processed
    #
    ### Recursive function to traverse the sequence of nodes (the graph) visiting each node once and
    ### running it's accompanied process function.
    ################################################################################################

    def run_node(self, node, results=None):
        """ Called on each node, and recursively on each child node """
        if results is None:
            results = {}

        if all(node.ready.values()):
            
            self.signals.nodeStart.send(self, name = node.node_id)
            node.global_vars = self.global_vars
            results[node] = node.process()
            self.global_vars = node.global_vars
            self.signals.nodeComplete.send(self, name = node.node_id)

            if len(node.events_fired) > 0:
                for event_id in node.events_fired:
                    event_data = node.events_fired[event_id]
                    self.resolve_event(event_id, event_data)
                node.events_fired = {}

            if node in self.nodes: # if this is a parent of another node
                for parent_terminal, child_terminal, child in self.nodes[node]:
                    if parent_terminal in results[node]:
                        child.args[child_terminal] = results[node][parent_terminal]
                        child.ready[child_terminal] = True
                        self.run_node(child, results)
            node.reset()

        return results, node.done
    
    def resolve_event(self, event_id, event_data):
        if event_id in self.event_callbacks:
            for callback in self.event_callbacks[event_id]:
                callback(event_id, event_data)


# result = pipeline.run(node)
# pipeline.run(node.child[0])