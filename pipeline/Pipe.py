class Pipe():

    """
    Pipes connect nodes/tasks keeping track of how to resolve data flow.
    For instance, one end of a pipe connects to something called out, the other end connects to named file_type
    the tasks themselves shouldnt need to worry about how this is handled, but something needs to resolve the differences.

    """

    def __init__(self, upstream, downstream):
        """ this is basically just an array... """
