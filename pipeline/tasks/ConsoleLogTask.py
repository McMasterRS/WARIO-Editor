from Task import Task

class ConsoleLogTask(Task):
    def run(self, upstream):
        
        print("Console Log: ", upstream)

        return upstream