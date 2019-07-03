from pipeline.Node import Node

class BatchedTask(Node):
    """ Batched tasks hold their data until the end of the entire batch """

    state = {} # State as maintained accross runs.