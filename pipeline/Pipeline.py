from collections import deque
from Task import Task
import json

from tasks import *

class Pipeline():
    
    """
    proccess flow pipeline. Oversees/orchestrates the running of a directed graph of arbitrary tasks
    
    """

    tasks = {}
    graph = {}         # Each connection, indexed by parent node. edges are always between two task nodes
    roots = {}         # Nodes with no parents
    leaves = []        # Nodes with no children
    results = {}

    def __init__(self):
        
        """
        initializes a pipeline, optionally with a set of nodes
        
        """

    def add_task(self, task, children=None, parents=None, type=None):
        
        """
        add a single task to the pipeline
        
        """

        self.tasks[task.name] = task
        self.graph[task.name] = {}
        self.results[task.name] = []
        if parents is None:
            self.roots[task.name] = task

    def connect(self, parent, child):

        self.graph[parent.name][child.name] = child

        # if the parent was a leaf node, remove it.
        if parent.name in self.leaves:
            self.leaves.pop(parent.name)

        # if the child was a root node, remove it.
        if child.name in self.roots:
            self.roots.pop(child.name)
    
    def _topological_sort(self, node, visited, queue):
        visited[node.name] = node
        for i in self.graph[node.name]:
            if i not in visited:
                self._topological_sort(self.tasks[i], visited, queue)
        queue.append(node)
        print(node.name)

    def topological_sort(self):

        visited = {}
        queue = []

        for root in self.roots:
            self.results[root] = [0]
            if self.roots[root] not in visited:
                self._topological_sort(self.roots[root], visited, queue)
        
        return queue

    def start(self, ):

        # sort the tasks in the correct order so that all dependancies are fulfilled

        ordered_tasks = self.topological_sort()

        # pops each task off the stack and runs it
        
        print('---')
        while len(ordered_tasks) > 0:

            task = ordered_tasks.pop()
            print("Running: ", task.name)
            # we get the approprate incoming data
            result = task.run(self.results[task.name])
            print("Result: ", result)

            for child in self.graph[task.name]:
                self.results[child].append(result)

    # TODO: Assumes a well formatted json file, should validate this
    def from_nodz(self, nodz_json):

        for node in nodz_json["NODES"]:
            self.add_task(Task(node), type=nodz_json["NODES"][node]["type"])

        for connection in nodz_json["CONNECTIONS"]:
            self.connect(self.tasks[connection[0].split(".")[0]], self.tasks[connection[1].split(".")[0]])

    def read_nodz(self, file_location):
        with open(file_location, 'r') as f:
            d = json.load(f)
            self.from_nodz(d)
