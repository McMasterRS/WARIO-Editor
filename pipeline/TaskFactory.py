import importlib

# Task Factories know about all types of tasks that can be created and creates the appropriate instance when called
class TaskFactory():

    loaded = {}

    def __init__(self, type_list):
        """ Upon creation, import just the tasks we need """
        # importlib
        for task_type in type_list:
            try:
                self.loaded[task_type] = importlib.import_module('tasks.%s' % task_type, "tasks")
                self.loaded[task_type] = getattr(self.loaded[task_type], task_type)
            except NotImplementedError:
                print("This is not a module I know")

    def create_task(self, task_type, task_id):
        return self.loaded[task_type](task_id)