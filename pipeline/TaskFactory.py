from Task import Task
import importlib

# Task Factories know about all types of tasks that can be created and creates the appropriate instance when called
class TaskFactory():

    task_types = {}

    def __init__(self):
        """ Upon creation, import just the tasks we need """

    def create_task(self, task_type):
        return self.task_types[task_type]