from Task import Task

class ReadFileTask(Task):
    def run(self, file_location, writable=False):

        data = []

        with open(file_location, 'r') as F:
            data = F.readlines()
        
        return data