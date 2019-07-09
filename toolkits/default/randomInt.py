from pipeline.Node import Node
import random

class randomInt(Node):

    def __init__(self, name):
        super(randomInt, self).__init__(name)
        
    def process(self, min=0, max=10):
        return {"Out": int(random.randrange(min, max))}