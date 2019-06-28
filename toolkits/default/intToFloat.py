from Task import Task

class intToFloat(Task):
    def run(self, upstream_int):
        return float(upstream_int)