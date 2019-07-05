from pipeline.Task import Task

class floatOut(Task):

    def __init__(self, name):
        super(floatOut, self).__init__(name)
        
    def run(self, floatIn):
        print("Float: ", floatIn)
        return floatIn