from pipeline.Task import Task

class intToFloat(Task):

    def __init__(self, name):
        super(intToFloat, self).__init__(name)
        
    def run(self, intIn):
        return {"Out": float(intIn)}