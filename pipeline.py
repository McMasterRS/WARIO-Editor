from pipeline.Node import CSVInputGUINode, CSVOutputGUINode
from pipeline.NodzInterface import NodzInterface
from pipeline.Pipeline import Pipeline
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog
from PyQt5.QtGui import QIcon


# nodes, connections, global_vars = NodzInterface.load("./pipeline/saves/sample.json")
# pipeline = Pipeline()

# for node_id, node in nodes:
#     pipeline.add(node)

# print("connections")
# for connection in connections:
#     parent, child = connection
#     pipeline.connect(parent, child)
#     # print("connect", parent, child)
#     # pipeline.connect(parent, child)

pipeline = Pipeline()
csv_in = CSVInputGUINode('a')
csv_out = CSVOutputGUINode('b')
pipeline.add(csv_in)
pipeline.add(csv_out)
pipeline.connect(parent=(csv_in, 'OUT'), child=(csv_out, 'IN'))
pipeline.start()




# from pipeline.TaskFactory import TaskFactory
# from pipeline.ImportLayer import NodzImporter
# from pipeline.Pipeline import Pipeline
# from pipeline.Node import TestImportNode, TestAddNode, TestNode
# from inspect import signature


# default_toolkit = Toolkit('default')

# for node in default_toolkit.nodes:
#     NodeFactory.register_node(node, default_toolkit.import_node(node))

# from pipeline.NodzInterface import NodzInterface



# nodz = NodzInterface()
# nodes, factory = nodz.load_pipeline_fs("pipeline/saves/sample.json")

# NODZ_SAVE_LOCATION = "saved.json"

# nodes, factory = NodzInterface.load_pipeline_fs(NODZ_SAVE_LOCATION)

# pipeline.add(nodz_save.nodes)
# pipeline.connect(nodz_save.connections)


# task_types, tasks, connections, configuration = NodzImporter().parsed
# factory = TaskFactory(task_types)
# pipeline = Pipeline()

# new_tasks = {}
# importtest = TestImportNode('A')
# printtest = TestNode('B')
# pipeline.add(importtest)
# pipeline.add(printtest)
# pipeline.connect(importtest, printtest, 'out', 'in')

# # print(configuration)

# for task_id in tasks:
#     task = factory.create_task(tasks[task_id]['type'], task_id)

#     for terminal in tasks[task_id]['in']:
#         task.ready[terminal] = False

#     if task_id in configuration:
#         for value in configuration[task_id]:
#             task.state[value] = configuration[task_id][value]
#             task.ready[value] = True

#     print("configured state", task.ready)
#     pipeline.add(task)
#     new_tasks[task_id] = task

# for parent_id in connections:
#     for parent_terminal in connections[parent_id]:
#         for child_id, child_terminal in connections[parent_id][parent_terminal]:        
#             pipeline.connect(new_tasks[parent_id], new_tasks[child_id], parent_terminal, child_terminal)


# pipeline.start()