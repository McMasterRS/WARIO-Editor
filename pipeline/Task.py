class Task():

    """
    A single atomic task, single tasks have no state themselves and rely on icoming data and a pipeline to orchestrate it's operation.
    Each task by default simply passes data through itself. But users can override the begin, run, and end functions to operate on the data.
    
    """

    def __init__(self, name, pipeline=None):
        self.name = name

    def _begin(self, incoming=None):

        """
        Internal begin hook, this is called as part of a pipeline's operation first before the task is run
        
        """

        return self.begin(incoming)

    def _run(self, incoming):

        """
        Internal run hook, the primary function called as part of a pipeline's operation. Runs user's code
        
        """

        return self.run(incoming)

    def _end(self, outgoing):

        """
        Internal end hook, this is called as part of a pipeline's operation after the task is run
        
        """

        return self.end(outgoing)        
    
    def begin(self, incoming):

        """
        Overwritable begin hook, this is called by the internal begin hook

        """

        return incoming

    def run(self, incoming):

        """
        Overwritable run hook, this is called by the internal run hook
                
        """
        print(self.name, incoming)
        return incoming

    def end(self, outgoing):

        """
        Overwritable end hook, this is called by the internal end hook
                
        """
        return outgoing