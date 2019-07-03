from pipeline.Task import Task

class intToFloat(Task):
    def run(self, intIn):
        return {"Out": float(intIn)}