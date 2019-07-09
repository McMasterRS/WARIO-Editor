from pipeline.Node import Node
import random

class randomFloat(Node):

    def __init__(self, name):
        super(randomFloat, self).__init__(name)
        
    def run(self, min=0, max=10):
        return float(random.randrange(min, max))