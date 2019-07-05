from pipeline.Task import Task
import random

class randomFloat(Task):

    def __init__(self, name):
        super(randomFloat, self).__init__(name)
        
    def run(self, min=0, max=10):
        return float(random.randrange(min, max))