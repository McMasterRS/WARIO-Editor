from Task import Task

class TestA(Task):

    def run(self):
        return {
            'A': 'A',
            'B': 'B'
        }