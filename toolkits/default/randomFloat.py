from pipeline.Task import Task
import random

class randomFloat(Task):
    def run(self, min=0, max=10):
        return float(random.randrange(min, max))