import importlib

# Task Factories know about all types of tasks that can be created and creates the appropriate instance when called
# Abstracts the creation logic, and all of the library importing away from the user
class TaskFactory():

    loaded = {}

    def __init__(self, type_list):
        """ Upon creation, import just the tasks we need """

        for task_type in type_list:
    
            try:
                self.loaded[task_type] = importlib.import_module('toolkits.default.' + type_list[task_type])
                self.loaded[task_type] = getattr(self.loaded[task_type], type_list[task_type])

            except NotImplementedError:
                print("This is not a module I know")

    def create_task(self, task_type, task_id):
        task = self.loaded[task_type](task_id)
        print("creating", task, task.ready)
        return task

class NodeFactory():
 
    registered_nodes = {}

    @classmethod
    def register_node(cls, type_id, type_class):
        cls.registered_nodes[type_id] = type_class
        print("Factory Register: ", type_class)

    @classmethod
    def create_node(cls, node_id, type_id):
        node = cls.registered_nodes[type_id](node_id)
        return node

    @classmethod
    def import_node(cls, type_id, toolkit_id, class_name):
        if type_id not in cls.registered_nodes:
            module_name = "toolkits." + toolkit_id + '.' + class_name
            module = importlib.import_module(module_name)
            cls.register_node(type_id, getattr(module, class_name))

        return cls.registered_nodes[type_id]