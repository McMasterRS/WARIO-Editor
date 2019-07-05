from pipeline.Task import Task

class intAdder(Task):
    def __init__(self, name):
        super(intAdder, self).__init__(name)

        self.nodz_translation = {
            "In A": "inA",
            "In B": "inB"
        }

    def run(self, inA, inB):
        return {"Out": inA + inB}