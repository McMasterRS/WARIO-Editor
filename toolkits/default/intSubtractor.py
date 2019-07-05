from pipeline.Task import Task

class intSubtractor(Task):

    def __init__(self, name):
        super(intSubtractor, self).__init__(name)

    def run(self, inA, inB):
        return inA-inB