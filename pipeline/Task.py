class Task():

    """
    A single atomic task, single tasks have no state themselves and rely on icoming data and a pipeline to orchestrate it's operation.
    Each task by default simply passes data through itself. But users can override the begin, run, and end functions to operate on the data.
    
    """

    def __init__(self, name, *args):
        self.name = name

    # TODO: Think about how this is passing arguments in.
    # Lets say someone wants to pass in the minimum and the maximum values to a function.
    # they can define it as Task.run(self, min, max, item=None), this could simply ignore the input, and return a random value between.
    # Should we instead use named arguments, we can't assume consistent ordering when they are coming in from the interface.
    # Or can we, we really should be starting a standard specification so that the front and back ends communicate effectively
    # A common interface description should mean that we can garentee this somewhat. but is it worth it?
    # Lets just try both.
    def _begin(self, incoming, *args):

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
    
    def begin(self, incoming, *arg):

        """
        Overwritable begin hook, this is called by the internal begin hook

        """

        return incoming

    def run(self, *arg, item=None):

        """
        Overwritable run hook, this is called by the internal _run hook.
                
        """
        print(self.name, item)
        return item

    def end(self, outgoing):

        """
        Overwritable end hook, this is called by the internal end hook
                
        """
        return outgoing