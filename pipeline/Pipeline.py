import json
from Task import Task

class Pipeline():
    
    """
    Proccess flow pipeline. Oversees/orchestrates the running of a directed graph of arbitrary tasks
    
    """

    tasks = {}      # Record of all the tasks loaded into the pipeline. Indexed by task.id.
    roots = {}      # Nodes with no parents. Updated as needed when new tasks are added, reduces need to search the whole graph
    leaves = []     # Nodes with no children. Updated as needed when new tasks are added, reduces need to search the whole graph
    upstream_state = {}         # Holding variable for upstream tasks to load their results. This will automatically be consumed into the direct child's arguments when it is run.
    upstream_connections = {}   # Shallow tree of each tasks direct children. Only one ever one child deep to simplofy traversing complex trees

    def __init__(self, tasks=None):
        
        """
        initializes a pipeline, optionally with a set of tasks
        
        """

    def add_task(self, task, children=None, parents=None, type=None):
        
        """
        add a single task to the pipeline
        
        """

        self.tasks[task.name] = task                # initializes itself into the task dictionary
        self.upstream_connections[task.name] = {}   # initializes itself into the connections hierarchy
        self.upstream_state[task.name] = []         # initializes an upstream state for itself

        # if this task has no parents, by definition it is a root node
        if parents is None:
            self.roots[task.name] = task
        
        # if this task has no children, by definition it is a leaf node
        # if children is None:
        #     self.roots[task.name] = task

    def connect(self, parent, child):

        # inserts the child downstream of the parent
        self.upstream_connections[parent.name][child.name] = child

        # if the parent was a leaf node, remove it.
        if parent.name in self.leaves:
            self.leaves.pop(parent.name)

        # if the child was a root node, remove it.
        if child.name in self.roots:
            self.roots.pop(child.name)
    
    def _topological_sort(self, node, visited, queue):

        """
        Recursive helper function to sort the graph of tasks into running order respectful of dependance.
        """

        visited[node.name] = node # marks a node as visited, allows it to only run once per node

        # Iterates through each child of this task, if it hasnt already been visited we want to traverse through it's children as well.
        for i in self.upstream_connections[node.name]:
            if i not in visited:
                self._topological_sort(self.tasks[i], visited, queue)

        # Enqueues the node into what will be the resulting running order
        queue.append(node)

    def topological_sort(self):
        """
        Starts the recursive depth first sorting of each task into a sequential sequence respecting parent child relationships. O(V+E)
        
        """

        visited = {}    # Record of what nodes have been visited
        queue = []      # Final running order of the tasks

        # starting at the top with our known roots, recurse through the tree of tasks
        for root in self.roots:
            if self.roots[root] not in visited:
                self._topological_sort(self.roots[root], visited, queue)
        
        return queue # returns an iteratible queue of task objects in correct running order

    def start(self, *args):
        """ 
        Starts the processing of the pipeline.
        """

        # Sort the tasks in the correct order so that all upstream data dependancies are fulfilled.
        # TODO: Right now, this is done each time the pipeline is started in case there were changes to the topology. Consider alternatives

        ordered_tasks = self.topological_sort()
        # task = ordered_tasks.pop()
        # task._run(*args) # Runs all root nodes with the arguments passed into the pipeline at the start.

        print('---')

        while len(ordered_tasks) > 0:

            task = ordered_tasks.pop()
            
            print("Running: ", task.name)

            if(task.name in self.roots):
                result = task.run(*args)
            else:
                result = task.run(self.upstream_state[task.name])
            
            # Each tasks incoming data is stored in that tasks respective spot

            print("Result: ", result)

            for child in self.upstream_connections[task.name]:
                self.upstream_state[child].append(result)

            print(self.upstream_state)

    def run_task(self, task):
        result = task.run(task.data)
        return result

    # TODO: Assumes a well formatted json file, should validate this.
    # TODO: Much better name for this function
    def from_nodz(self, nodz_json):

        for node in nodz_json["NODES"]:
            self.add_task(Task(node), type=nodz_json["NODES"][node]["type"])

        for connection in nodz_json["CONNECTIONS"]:
            self.connect(self.tasks[connection[0].split(".")[0]], self.tasks[connection[1].split(".")[0]])

    def read_nodz(self, file_location):
        with open(file_location, 'r') as f:
            d = json.load(f)
            self.from_nodz(d)

