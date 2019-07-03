from pipeline.Task import Task

class intMultiplier(Task):    
    def run(self, inA, inB):
        return {"Out": inA*inB}