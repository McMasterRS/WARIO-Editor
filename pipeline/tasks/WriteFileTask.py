from Task import Task

class WriteFileTask(Task):
    def run(self, file_location, data):

        file = open(file_location, 'w')
        file.write(data) 
        file.close() 

        return file