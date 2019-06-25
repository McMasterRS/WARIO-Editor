from ..Task import Task
import random

class RandomTask(Task):
    def run(self, min, max):
        return random.randrange(min, max)