from pipeline.Task import Task

class intDividerR(Task):

    def __init__(self, name):
        super(intDividerR, self).__init__(name)
        
    def run(self, inA, inB):
        return inA/inB