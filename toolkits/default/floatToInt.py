from pipeline.Task import Task

class floatToInteger(Task):
    def run(self, floatIn):
        return {int(floatIn)}