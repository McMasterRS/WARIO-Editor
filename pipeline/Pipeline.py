import json

    #######
    #
    #
    #
    #######

class Pipeline():
    """  Proccess flow pipeline. Oversees/orchestrates the running of a directed graph of arbitrary tasks  """

    tasks = {}          # Record of all the tasks loaded into the pipeline. Indexed by task.id, this also has each tasks single level deep children?
    pipes = {}          # Pipes connect upstream tasks with their approprate downstream attributes. Pipes also keep data stored when a task must wait for multiple upstream dependancies. Could queue them?
    state = {}          # The upstream state of all nodes. This is where parents store their results once they finish   

    roots = {}          # Nodes with no parents. Updated as needed when new tasks are added, reduces need to search the whole graph
    leaves = {}         # Nodes with no children. Updated as needed when new tasks are added, reduces need to search the whole graph

    #######
    #
    # 
    #
    #######

    def __init__(self, tasks=None, pipes=None):
        """  initializes a pipeline, optionally with a set of tasks  """

    #######
    #
    # Pipeline.add: Adds a single task to the pipeline, not connected to any other tasks and is both a root and leaf node
    # - task: the task you want to add to the pipeline
    #
    # TODO: allow you to add multiple tasks at once
    # TODO: allow you to initialize them with children and parents (this was in but removed for simplicity when attributes were added)
    #
    #######

    def add(self, task, params=None):

        """  add a single task to the pipeline  """

        self.tasks[task.name] = task    # Store the task, indexed by name/id
        self.roots[task.name] = task    # 
        self.leaves[task.name] = task   #
        self.pipes[task.name] = {}      # Initializes a dictionary for collecting the task's upstream data.
        self.state[task.name] = {}

        # print(type(params))
        if params is not None:
            for param in params:
                self.state[task.name][param] = params[param]

    #######
    #
    # Pipeline.connect: connects a parent with a child along their respective attributes so that when it runs it correctly passes its results downstream
    # - parent: The task that will act as the upstream parent
    # - child: The task that will be downstream and recieving the parents results
    # - parent_attrib: the outgoing attribute on the parent's side, this will match the associating attribute on the child
    # - child_attrib: the incoming attribute on the child's side, this will match the associated attribute on the parent
    #
    #######

    def connect(self, parent_name, child_name, parent_attrib, child_attrib):

        """  Connect two nodes along the specified attributes. Data output by the parent will collect for the child on that attribute.  """

        # store the relationship so the parent can reference it
        self.pipes[parent_name][parent_attrib] = [parent_name, child_attrib]

        # store the relationship so the parent can reference it
        self.pipes[child_name][child_attrib] = [child_name, parent_attrib]

        # if the parent was a leaf node, since it has children now, it no longer is.
        if parent_name in self.leaves:
            self.leaves.pop(parent_name)

        # if the child was a root node, since it has a parent now, it no longer is.
        if child_name in self.roots:
            self.roots.pop(child_name)

    #######
    #
    # Pipeline.topological_sort: internally sorts the tasks in to a linear sequence respectful of each tasks dependacies
    # TODO: Right now, this is done each time the pipeline is started in case there were changes to the topology. Consider alternatives
    #
    #######

    def topological_sort(self):

        """ Starts the recursive depth first sorting of each task into a sequential sequence respecting parent child relationships. O(V+E) """

        ####
        #
        # Recursive helper function for topological sorting
        #
        ####
        def sort(node, visited, queue):

            """ Recursive helper function to sort the graph of tasks into running order respectful of dependance. """

            # marks a node as visited, allows it to only run once per node. The check simply checks for its presence in this dictionary
            visited[node.name] = True

            # Iterates through each child of this task, if it hasnt already been visited we want to traverse through it's children as well.
            for attribute in self.pipes[node.name]: # i is the attribute
    
                # retrives the child that is downstream from that attribute. We only want the task not the attribute hence the [0]
                child = self.pipes[node.name][attribute][0]

                # if the child hasnt been visited, visit it and sort it's children as well. 
                if child not in visited:
                    sort(self.tasks[child], visited, queue)

            # Enqueues the node into what will be the resulting running order
            queue.append(node)


        # Record of what nodes have been visited
        visited = {}    
        
        # Final running order of the tasks
        queue = []      

        # starting at the top with our known roots, recurse through the tree of tasks
        for root in self.roots:
            if self.roots[root] not in visited:
                sort(self.roots[root], visited, queue)
        
        return queue # returns an iteratible queue of task objects in correct running order

    #######
    #
    # pipeline.start: 
    #
    #######

    def start(self, *args, **kwargs):

        """  Starts the processing of the pipeline.  """

        # Sort the tasks in the correct order so that all upstream data dependancies are fulfilled.
        ordered_tasks = self.topological_sort()

        while len(ordered_tasks) > 0:
            
            # Retrieves the next task to run from the end of the queue
            task = ordered_tasks.pop() 

            # Runs the task using the available upstream data.
            print("Running: ", task.name, self.state[task.name])
            results = task.run(**self.state[task.name])
            print("Result: ", results)
            
            # Stores its results in the approprate attribute location of it's children downstream
            if type(results) is dict:
                for attribute in results:
                    self.push(task, attribute, results[attribute])

    #######
    #
    # Pipeline.Push: resolves the downstream passing of data between a parent and it's children along a particular attribute.
    # - task: The upstream task that has some data to pass
    # - attribute: The attribute along which the task is trying to pass data
    # - data: the results of the tasks particular computation that is to be passed to it's child
    #
    #######

    def push(self, task, attribute, data):

        """  Resolves the transfer of data out of a task and into the appropriate downstream locations.  """

        print(self.pipes, task.name, attribute)
        if attribute in self.pipes[task.name]:

            # look up what nodes are downstream and what it connects to.
            child, child_attribute = self.pipes[task.name][attribute]

            # stores the data in that childs respective attribute, ready to be consumed when the child runs.
            self.state[child.name][child_attribute] = data
