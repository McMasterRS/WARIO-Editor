from pipeline.Task import Task

class intMultiplier(Task):    

    def __init__(self, name):
        super(intMultiplier, self).__init__(name)
        
    def run(self, inA, inB):
        return {"Out": inA*inB}