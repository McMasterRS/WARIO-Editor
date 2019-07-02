from pipeline.Task import Task

class intSubtractor(Task):
    def run(self, inA, inB):
        return inA-inB