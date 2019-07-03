from pipeline.Task import Task

class intAdder(Task):

    nodz_translation = {
        "In A": "inA",
        "In B": "inB"
    }

    def run(self, inA, inB):
        return {"Out": inA + inB}