from pipeline.Task import Task
import random

class randomInt(Task):

    def __init__(self, name):
        super(randomInt, self).__init__(name)
        
    def run(self, min=0, max=10):
        return {"Out": int(random.randrange(min, max))}