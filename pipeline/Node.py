from inspect import signature, Parameter
from collections import OrderedDict
from pipeline.TaskFactory import NodeFactory

###################################################################################################
# Node/Task
# + Abstract node for handling the running of a discrete task in a workflow
###################################################################################################

class Node():
    """ Abstract Node class. This describes a single operational function in our process pipeline """

    ################################################################################################
    # Node.__init__: Initializes the node
    # + node_id: The unique id for the node.
    ################################################################################################
    def __init__(self, node_id=None):
        """ Initialize Node """
        self.node_id = node_id  # identifier for the node
        self.ready = {}         # Flags for each argument, all true indicates the node should run
        self.state = {}         # Variables local to the node, set internally by itself. Persits
        self.args = {}          # Variables local to the node, set externally by it's parents
        self.global_vars = {}   # Variables global to the entire pipeline.
        self.done = True        # Flag indicating if this node requires multple passes

    ################################################################################################
    # Node.start: Pipeline runs this when the pipeline starts
    ################################################################################################
    def start(self):
        """ Default start hook ran by the pipeline before all processing begins """
        return None
        
    ################################################################################################
    # Node.start: Pipeline runs this when the node is ready
    ################################################################################################
    def process(self):
        """ Default process hook ran by the pipeline when this node is ready """
        return {}

    ################################################################################################
    # Node.reset: Pipeline runs this to reset this nodes state variables
    ################################################################################################    
    def reset(self):
        """ Default process hook ran by the pipeline to reset this node's state variables """
        return None
        
    ################################################################################################
    # Node.end: Pipeline runs this when the pipeline ends
    ################################################################################################    
    def end(self):
        """ Default end hook ran by the pipeline once the pipeline has finished """
        return None

    ################################################################################################
    # TODO: This can more intelligently be completed at each adding of data from upstream
    ################################################################################################
    def is_ready(self):
        ready = True
        for param in self.ready:
            ready = ready and param in self.state
        print(self, self.state, self.ready, ready)
        return ready