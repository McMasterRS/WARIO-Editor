import json

###################################################################################################
#
###################################################################################################

class Pipeline():
    """  Proccess flow pipeline. Oversees/orchestrates the running of a directed graph of arbitrary tasks  """

    tasks = {}          # Record of all the tasks loaded into the pipeline. Indexed by task.id, this also has each tasks single level deep children?
    pipes = {}          # Pipes connect upstream tasks with their approprate downstream attributes. Pipes also keep data stored when a task must wait for multiple upstream dependancies. Could queue them?

     # we need something, somewhere, that knows how to turn the nodz attribute names into function attribute names.
     # without that, right now, we assume the order of attributes coming in from nodz is correct, and the params handle named attributes
    state = {}          # The upstream state of all nodes. This is where parents store their results once they finish.
    params = {}         # perhaps temporary, stores each tasks params.

    roots = {}          # Nodes with no parents. Updated as needed when new tasks are added, reduces need to search the whole graph
    leaves = {}         # Nodes with no children. Updated as needed when new tasks are added, reduces need to search the whole graph

    input_nodes = []
    output_nodes = None
    batch_nodes = []
    run_nodes = []
    nodes = {}
    edges = {}

    ###################################################################################################
    #
    ###################################################################################################

    def __init__(self, tasks=None, pipes=None):
        """  initializes a pipeline, optionally with a set of tasks  """

    ###################################################################################################
    #
    # Pipeline.add: Adds a single task to the pipeline, not connected to any other tasks and is both a root and leaf node
    # - task: the task you want to add to the pipeline
    #
    # TODO: allow you to add multiple tasks at once
    # TODO: allow you to initialize them with children and parents (this was in but removed for simplicity when attributes were added)
    #
    ###################################################################################################

    def add(self, task, params=None, is_input_node=False, is_batch_node=False, is_run_node=False):

        """  add a single task to the pipeline  """

        self.tasks[task.name] = task    # Store the task, indexed by name/id
        self.roots[task.name] = task    # 
        self.leaves[task.name] = task   #
        self.pipes[task.name] = {}      # Initializes a dictionary for collecting the task's upstream data.
        self.state[task.name] = {}

        self.params[task.name] = {}

        self.nodes[task.name] = task

        # if this is an input node and there isn't already one, set it to be the input node
        if is_input_node:
            self.input_nodes.append(task)

        if is_batch_node:
            self.batch_nodes[task.name] = task

        if is_run_node:
            self.run_nodes[task.name] = task

        if params is not None:
                self.params[task.name] =  params
                # self.state[task.name][param] = params[param]

    ###################################################################################################
    #
    # Pipeline.connect: connects a parent with a child along their respective attributes so that when it runs it correctly passes its results downstream
    # - parent: The task that will act as the upstream parent
    # - child: The task that will be downstream and recieving the parents results
    # - parent_attrib: the outgoing attribute on the parent's side, this will match the associating attribute on the child
    # - child_attrib: the incoming attribute on the child's side, this will match the associated attribute on the parent
    #
    ###################################################################################################

    def connect(self, parent_name, child_name, parent_attrib, child_attrib):

        """  Connect two nodes along the specified attributes. Data output by the parent will collect for the child on that attribute.  """

        # print(parent_name, child_name, parent_attrib, child_attrib)

        # store the relationship so the parent can reference the child when passing data downstream
        if parent_attrib not in self.pipes[parent_name]:
            self.pipes[parent_name][parent_attrib] = []
            self.nodes[parent_name].edges[parent_attrib] = []

        self.pipes[parent_name][parent_attrib].append([child_name, child_attrib])
        self.nodes[parent_name].edges[parent_attrib].append([child_name, child_attrib])
        self.nodes[parent_name].children[child_name] = self.nodes[child_name]

        self.nodes[parent_name].downstream[parent_attrib] = [child_name, child_attrib]
        # self.nodes[child_name].upstream[child_attrib] = None
        
        # store the relationship so the child can reference the parent, if that is ever needed
        if child_attrib not in self.pipes[child_name]:
            self.pipes[child_name][child_attrib] = []

        self.pipes[child_name][child_attrib].append([parent_name, parent_attrib])

        # if the parent was a leaf node, since it has children now, it no longer is.
        if parent_name in self.leaves:
            self.leaves.pop(parent_name)

        # if the child was a root node, since it has a parent now, it no longer is.
        if child_name in self.roots:
            self.roots.pop(child_name)

    ###################################################################################################
    #
    # Pipeline.topological_sort: internally sorts the tasks in to a linear sequence respectful of each tasks dependacies
    # TODO: Right now, this is done each time the pipeline is started in case there were changes to the topology. Consider alternatives
    #
    ###################################################################################################

    def topological_sort(self):

        """ Starts the recursive depth first sorting of each task into a sequential sequence respecting parent child relationships. O(V+E) """

        ###################################################################################################
        #
        # Recursive helper function for topological sorting
        #
        ###################################################################################################

        def sort(node, visited, queue):

            """ Recursive helper function to sort the graph of tasks into running order respectful of dependance. """

            # marks a node as visited, allows it to only run once per node. The check simply checks for its presence in this dictionary
            visited[node.name] = True

            # Iterates through each child of this task, if it hasnt already been visited we want to traverse through it's children as well.
            for attribute in self.pipes[node.name]:
                for child in self.pipes[node.name][attribute]:

                    # Retrives the child that is downstream from that attribute. We only want the task not the attribute hence the [0]
                    child_name = child[0]

                    # If the child hasnt been visited, visit it and sort it's children as well. 
                    if child_name not in visited:
                        sort(self.tasks[child_name], visited, queue)

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

    ###################################################################################################
    #
    # pipeline.start: 
    #
    ###################################################################################################

    def start(self):

        """  Starts the processing of the pipeline.  """

        # Sort the tasks in the correct order so that all upstream data dependancies are fulfilled.
        ordered_tasks = self.topological_sort()

        while len(ordered_tasks) > 0:
            
            # Retrieves the next task to run from the end of the queue
            task = ordered_tasks.pop() 

            # Runs the task using the available upstream data. Right now this unfortunately requires the order of the arguments to be correct
            print("Running: ", task.name, self.state[task.name], self.params[task.name])
            results = task.run(*self.state[task.name].values(), **self.params[task.name])
            print("Result: ", results)
            
            # Stores its results in the approprate attribute location of it's children downstream
            if type(results) is dict:
                for attribute in results:
                    self.push(task, attribute, results[attribute])

    ###################################################################################################
    #
    # Pipeline.Push: resolves the downstream passing of data between a parent and it's children along a particular attribute.
    # - task: The upstream task that has some data to pass
    # - attribute: The attribute along which the task is trying to pass data
    # - data: the results of the tasks particular computation that is to be passed to it's child
    #
    ###################################################################################################

    def push(self, task, attribute, data):

        """  Resolves the transfer of data out of a task and into the appropriate downstream locations.  """

        if attribute in self.pipes[task.name]:
            # since one outgoing attribute can connect to many incoming attributes, we loop through them all
            for child in self.pipes[task.name][attribute]:
                child_name = child[0]
                child_attribute = child[1]
                # stores the data in that childs respective attribute, ready to be consumed when the child runs.
                self.state[child_name][child_attribute] = data

    ###################################################################################################
    #
    # pipeline.start_batch: run a batch of inputs
    #
    ###################################################################################################

    def start_batch(self, input_node):
        batch = input_node.load_batch()
        self.process_batch(batch)

    ###################################################################################################
    #
    # pipeline.process_batch: run a batch of inputs
    #
    ###################################################################################################

    def process_batch(self, batch): # the batch is a set of files

        for run in batch:
            self.process_run(run)
        print("batch ended")

        for node in self.batch_nodes: ## this is all of the nodes that have been delayed until the end of the batch
            node.delay = False # open the node up to process it's children.
            self.process_node(node)

    ###################################################################################################
    #
    # pipeline.start_run: run a single run from a set of runs in a batch
    #
    ###################################################################################################

    def process_run(self, run): # the run is a single file

        for item in run:
            self.process_item(item)
        print("run ended")

        for node in self.run_nodes: ## this is all the nodes that have been delayed until the end of the run
            node.delay = False # open the node up to process it's children
            self.process_node(node, **self.state[node.name])


    ###################################################################################################
    #
    # pipeline.start_item: run a single item from a set of items in a run
    #
    ###################################################################################################

    def process_item(self, items): # the item is a row in a file

        for item in items:
            for root in self.roots:
                self.process_node(root, item)
        print("row ended")

    ###################################################################################################
    #
    # pipeline.process_node: run a node then recursively run that node's children if permitted
    #
    ###################################################################################################

    def process_node(self, node_name):
        node = self.nodes[node_name]

        print(*list(node.upstream.values()))

        # if the node is ready to run, run it
        if node.ready:
            print(node.upstream)
            # pass in the incoming arguments
            results = node._process(*list(node.upstream.values()))

            # resolve where this node is sends it's data
            for attribute in results:
                print("edge", attribute, node.downstream)
                if attribute in node.downstream:
                    print("edge", attribute, results)
                    child_name, child_attribute = node.downstream[attribute]
                    child = self.nodes[child_name]
                    print("child: ", child, child_attribute)
                    child.upstream[child_attribute] = results[attribute]
                    child.signature[child_attribute] = True # we want the child to know there is data waiting for it on that edge    
                    print("child: ", child, child_attribute, child.signature)
                    child.ready = self.is_node_ready(child)


            # if the node isnt delaying it's results, then we want to try running it's children.
            if not node.delay:
                for child in node.children:
                    print(child)
                    self.process_node(child)

    def is_node_ready(self, node):
        ready = False # assumes the node isnt ready.
        for attribute in node.signature:
            ready = ready and attribute #
        return ready

    def start_processing(self):
        # Loop through all of the input nodes, we need to load the batch data in first
        for node in self.input_nodes:
            node.batch = node.load_batch()
            while not node.batch_finished:
                self.process_node(node.name)

## Lets think this through.
## A pipeline can be initialized with some sort of batched data, but technically all data is a batch, even if it is a single item
## so you might have an input node, that consumes some amount of data then doles it out in parts
## most obvious example is a csv file, it consumes a directory, then 
