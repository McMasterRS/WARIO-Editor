from pipeline.Task import Task

class floatOut(Task):
    def run(self, floatIn):
        print("Float: ", floatIn)
        return floatIn