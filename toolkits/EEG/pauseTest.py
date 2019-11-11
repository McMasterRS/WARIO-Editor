from pipeline.Node import Node
import sys

class pauseTest(Node):

    def __init__(self, name, params):
        super(pauseTest, self).__init__(name, params)
        
    def process(self):
        t = input("Testing: type anything to continue")
        print("Done")
        return {}