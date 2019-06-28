from Task import Task
import random

class randomInt(Task):
    def run(self, minimum=0, maximum=10):
        return int(random.randrange(minimum, maximum))