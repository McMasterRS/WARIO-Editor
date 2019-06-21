class Node():

    """
    Describes a single operational node in a process pipeline.
    
    """

    def __init__(self, name, pipeline=None):

        self.name = name            # Unique identifier accross nodes
        self.state = {}             # State dictionary should this be necessary
        self.pipeline = pipeline    #
        self.results = None

        # if the node is initialized as part of a pipeline, add it to the pipeline
        if(self.pipeline is not None):
            self.pipeline.add_node(self)

    def begin(self):

        """
        Node lifecycle, called before processing begins for this node
        
        """

        if self.pipeline is not None :
            self.pipeline.node_beginning(self)

    def run(self):

        """
        Node lifecycle, called when processing inputs
        
        """

        self.begin()

        if self.pipeline is not None :
            self.pipeline.node_running(self)

        self.finish()

    def finish(self):

        """
        Node lifecycle, called once this node has finished processing it's inputs
        
        """

        # Reports back to the pipeline that it has finished processing        
        if self.pipeline is not None :
            self.pipeline.node_ended(self, self.results)