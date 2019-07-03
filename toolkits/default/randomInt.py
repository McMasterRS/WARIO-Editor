from pipeline.Task import Task
import random

class randomInt(Task):
    def run(self, min=0, max=10):
        return int(random.randrange(min, max))