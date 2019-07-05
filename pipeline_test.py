from pipeline.ImportLayer import NodzImporter
from pipeline.TaskFactory import TaskFactory
from pipeline.Pipeline  import Pipeline
from pipeline.Task import Task

from pipeline.Node import FileInputNode, PrintNode

INPUT = FileInputNode("input")
A = PrintNode("A")
B = PrintNode("B")

pipeline = Pipeline()
pipeline.add(INPUT, 'input')
pipeline.add(A, 'A')
pipeline.add(B, 'B', delay="run")
pipeline.connect('input', 'A', "out", "in")
pipeline.connect('input', 'B', "out", "in")

pipeline.process_input('input', {})

# pipeline.start_processing()

# task_types, tasks, connections = NodzImporter().parsed
# task_factory = TaskFactory(task_types)

# # simply loops through the loaded tasks and turns them into the appropriate Task classes
# for task_name in tasks:
#     task = task_factory.create_task(tasks[task_name]["type"], task_name)
#     pipeline.add(task, params=tasks[task_name]["paramaters"])

# for parent_name in connections:
#     for parent_attribute in connections[parent_name]:
#         for child in connections[parent_name][parent_attribute]:
#             child_name, child_attribute = child
#             pipeline.connect(parent_name, child_name, parent_attribute, child_attribute)
        
# pipeline.start()