class Node():

    """
    Describes a single operational node in a process pipeline.
    
    """

    def __init__(self, name, pipeline=None, fn=None):

        self.name = name            # Unique identifier accross nodes
        self.pipeline = pipeline    # The pipeline this node should be initialized as a part of
        self.results = None         # The results of the task that is completed by this node.
        self.fn = fn                # The task this node will complete when it is called

        # If the node has been initialized as part of a pipeline, tell the pipeline to add it.
        if(self.pipeline is not None):
            self.pipeline.add_node(self)

    # def _begin(self):

    #     """
    #     Node lifecycle, called before processing begins for this node.
        
    #     """
    #     if(getattr(self, 'begin')):
    #         self.begin() # call any overidden begin functionality

    #     # Report to the pipeline that the node is running
    #     if self.pipeline is not None :
    #         self.pipeline.node_beginning(self)

    # def _run(self):

    #     """
    #     Node lifecycle, called when processing inputs
        
    #     """

    #     self._begin()
    #     self.run()
    #     if self.pipeline is not None :
    #         self.pipeline.node_running(self)

    #     self._finish()

    # def _finish(self):

    #     """
    #     Node lifecycle, called once this node has finished processing it's inputs
        
    #     """
    #     self.finish()
    #     # Reports back to the pipeline that it has finished processing        
    #     if self.pipeline is not None :
    #         self.pipeline.node_ended(self, self.results)