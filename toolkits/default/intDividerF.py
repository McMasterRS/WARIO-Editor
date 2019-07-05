from pipeline.Task import Task

class intDividerF(Task):

    def __init__(self, name):
        super(intDividerF, self).__init__(name)
        
    def run(self, inA, inB):
        return inA/inB