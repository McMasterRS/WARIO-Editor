from Task import Task

class intOut(Task):
    def run(self, upstream_int):
        print("Float: ", upstream_int)
        return None