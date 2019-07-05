from pipeline.Task import Task

class intOut(Task):

    def __init__(self, name):
        super(intOut, self).__init__(name)

    def run(self, intIn):
        print("Float: ", intIn)
        return intIn