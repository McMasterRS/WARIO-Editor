from Task import Task

class floatOut(Task):
    def run(self, upstream_float):
        print("Float: ", upstream_float)
        return None