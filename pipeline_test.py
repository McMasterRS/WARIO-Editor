from pipeline.TaskFactory import TaskFactory
from pipeline.ImportLayer import NodzImporter
from pipeline.Pipeline import Pipeline
from pipeline.Node import TestImportNode, TestAddNode, TestNode
from inspect import signature


task_types, tasks, connections, configuration = NodzImporter().parsed
factory = TaskFactory(task_types)
pipeline = Pipeline()

new_tasks = {}

# print(configuration)

for task_id in tasks:
    task = factory.create_task(tasks[task_id]['type'], task_id)

    for terminal in tasks[task_id]['in']:
        task.ready[terminal] = False

    if task_id in configuration:
        for value in configuration[task_id]:
            task.state[value] = configuration[task_id][value]
            task.ready[value] = True

    print("configured state", task.ready)
    pipeline.add(task)
    new_tasks[task_id] = task

for parent_id in connections:
    for parent_terminal in connections[parent_id]:
        for child_id, child_terminal in connections[parent_id][parent_terminal]:        
            pipeline.connect(new_tasks[parent_id], new_tasks[child_id], parent_terminal, child_terminal)


pipeline.start()