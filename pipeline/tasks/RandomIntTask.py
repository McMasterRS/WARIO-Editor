from Task import Task
import random


class RandomIntTask(Task):
    """
    Simple example task, this takes arguments (min and max),
    Simply ignores upstream dadta and returns a single random integer

    """

    def run(self, *args, minimum=0, maximum=10):
        """ Accepts any input arguments, but does nothing with them. If a minimum or a maximum are defined use that to configure """
        return random.randrange(minimum, maximum)