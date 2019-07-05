from pipeline.Task import Task

class floatToInteger(Task):

    def __init__(self, name):
        super(floatToInteger, self).__init__(name)
        
    def run(self, floatIn):
        return {int(floatIn)}