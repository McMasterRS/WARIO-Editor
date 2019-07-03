from pipeline.Task import Task

class intOut(Task):
    def run(self, intIn):
        print("Float: ", intIn)
        return intIn