from Task import Task

# something about signature, blah blah blah
class HelloTask(Task):
    def begin(self, message):
        print(self.name, "BEGINS")
    def run(self, message):
        print(self.name, "RUNNING", message)
