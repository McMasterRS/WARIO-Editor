from pipeline.Task import Task
import random

class randomFloat(Task):
    def run(self, minimum=0, maximum=10):
        return float(random.randrange(minimum, maximum))