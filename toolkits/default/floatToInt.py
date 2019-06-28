from Task import Task

class floatToInteger(Task):
    def run(self, upstream_float):
        return int(upstream_float)