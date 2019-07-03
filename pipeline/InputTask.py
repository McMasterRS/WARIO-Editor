from pipeline.Task import Task

class InputTask(Task):

    """ this is some sort of task that inputs things therefore it takes no arguments and send partial data periodically """
    
    def __init__(self):
        pass

class FileInputTask(InputTask):

    """ prompts the user for a set of files. then sends downstream nodes it one per line """

    def __init__(self):
        pass