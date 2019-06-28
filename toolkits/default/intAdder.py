from pipeline.Task import Task

class intAdder(Task):
    def run(self, inA, inB):
        return inA + inB