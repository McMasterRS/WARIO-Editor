class Task():

    """
    A single atomic task, single tasks have no state themselves and rely on icoming data and a
    pipeline to orchestrate it's operation. Each task by default simply passes data through itself.
    But users can override the begin, run, and end functions to operate on the data.
    """

    def __init__(self, name, *args):
        self.name = name

    # TODO: Think about how this is passing arguments in.

    # Configuration is named variables, positional arguments are the incoming data
    def _run(self, *arg, **kwargs):

        """
        Internal run hook, the primary function called as part of a pipeline's operation. Runs user's code
        
        """
        item = self.begin(*arg, **kwargs)
        item = self.run(*arg, **kwargs)
        item = self.end(*arg, **kwargs)
        return item

    def begin(self, *args, **kwargs):

        """
        Overwritable begin hook, this is called by the internal _run hook

        """

        return args

    def run(self, *args, **kwargs):

        """
        Overwritable run hook, this is called by the internal _run hook.
                
        """
        print(self.name, args)
        return args

    def end(self, *args, **kwargs):

        """
        Overwritable end hook, this is called by the internal _run hook
                
        """
        return args