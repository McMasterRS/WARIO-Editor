from Task import Task
class BatchedTask(Task):

    """ Type of task that needs to remember some sort of state between runs """

    state = {}
    
    def __init__(self, name, n, pipeline=None):
        pass
        # super(BatchedTask, )
