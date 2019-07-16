from inspect import signature, Parameter
from collections import OrderedDict
from pipeline.TaskFactory import NodeFactory

###################################################################################################
# Node/Task
# + Abstract node for handling the running of a discrete task in a workflow
###################################################################################################

class Node():
    """ Abstract Node class. This describes a single operational function in our process pipeline """

    ################################################################################################
    ################################################################################################
    def __init__(self, node_id=None):

        self.node_id = node_id  # identifier for the node
        self.ready = {}         # Flags for each argument, all true indicates the node should run
        self.state = {}         # Variables local to the node, set internally by itself. Persits
        self.args = {}          # Variables local to the node, set externally by it's parents
        self.global_vars = {}       # Variables global to the entire pipeline.
        self.done = True        # Flag indicating if this node requires multple passes

    ################################################################################################
    ################################################################################################
    def start(self):
        return None
        
    ################################################################################################
    ################################################################################################
    def process(self):
        return {}

    ################################################################################################
    ################################################################################################    
    def reset(self):
        return None
        
    ################################################################################################
    ################################################################################################    
    def end(self):
        return None

    ################################################################################################
    # TODO: This can more intelligently be completed at each adding of data from upstream
    ################################################################################################
    def is_ready(self):
        ready = True
        for param in self.ready:
            ready = ready and param in self.state
        print(self, self.state, self.ready, ready)
        return ready

class TestImportNode(Node):

    def start(self):
        self.data = [0,1,2,3,4,5,6,7,8,9]
        self.done = False

    def process(self):
        if len(self.data) == 0:
            self.done = True
            return { 'out': None}

        return {
            'out': self.data.pop()
        }

class TestAddNode(Node):
    def process(self, A, B):
        print(A, B)
        return {
            'out': A + B
        }

class TestNode(Node):
    def process(self):
        return {
            'A': 0, 'B': 1
        }

###################################################################################################
#
###################################################################################################

# class InputNode(Node):
#     """ Node that returns part of its data each time it's run """

#     batch = []  # The complete set of data for a process to run. A directory of one or more files.
#     run = [] # A subset of a batch, a set of rows in a file for example
#     row = [] # A subset of a run, an single row in a file for example
#     value = None

#     batch_finished = False
#     run_finished = False
#     row_finished = False
#     ready = False

#     def load_batch(self):
#         return [[[]]]

#     # this is part of the running code, it consumes the next piece of data, then pushes it onwards
#     def process(self, *args, **kwargs):
#         self.value = None

#         # This is the process of iterating through and processing the batch, run, and row data
#         if len(self.row) == 0: # this is the last one in the row
#             self.row_finished = True
#             if len(self.run) == 0: # this is the last one in the run
#                 self.run_finished = True
#                 if len(self.batch) == 0: # this is the last one in the batch
#                     self.batch_finished = True
#                 else: # there is still some left in the batch
#                     self.run = self.batch.pop()
#                     self.row = self.run.pop()
#                     self.value = self.row.pop()
#                     self.run_finished = False
#                     self.row_finished = False
#             else: # there is still som left in the run
#                 self.row = self.run.pop()
#                 self.value = self.row.pop()
#                 self.row_finished = False
#         else:
#             self.value = self.row.pop() # we wouldnt be running this if there was nothing in the row

#         # print(self.row)

#         return {
#             "out": self.value
#         }

# ###################################################################################################
# #
# ###################################################################################################

# class OutputNode(Node):
#     """ abstract node with no children, this is used to output the results of the entire process """
    
#     def finish_batch(self, batch):
#         """ concludes the running of a batch of runs """
    
#     def finish_run(self, run, batch):
#         """ concludes the running of a run """

#     def output_after_batch(self, batch):
#         return batch

#     def output_after_run(self, run):
#         return run

# ###################################################################################################
# #
# ###################################################################################################

# class FileInputNode(InputNode):
#     """ This is an input node where each item is a row of a file or each row in a set of files. """ 

#     def load_batch(self, batch=[]):
#         """ load the data for the whole batch, in this case, a set of files """ 

#         file_locations = self.prompt_file_locations()
#         for location in file_locations:
#             batch.append(self.read_file(location))

#         return batch

#     def prompt_file_locations(self):
#         """ prompt the user with a graphical file selector """
        
#         file_locations = ["./test1.csv", "test2.csv"]

#         return file_locations

#     def read_file(self, file_location):
#         """ reads all of the data from a set of file locations. returns the raw data """

#         data = []

#         with open(file_location) as f:
#             data = list(csv.reader(f))

#         return data

# ###################################################################################################
# #
# ###################################################################################################

# class RandomInputNode(InputNode):
#     """ fills a set of columns and rows with random numbers and pushes them as a batch and runs """

#     def __init__(self, n_rows=0, n_columns=0, rand_min=0, rand_max=1, precision=3):
#         self.n_rows = n_rows
#         self.n_columns = n_columns
#         self.rand_min = rand_min
#         self.rand_max = rand_max
#         self.precision = precision

#     def load_batch(self, batch=[]):
#         batch = [[random.randrange(self.rand_min, self.rand_max) for i in range(self.n_columns)] for j in range(self.n_rows)]
#         return batch

# ###################################################################################################
# #
# ###################################################################################################
# class PrintNode(Node):

#     def process(self, value):
#         print("PRINTNODE: ", value)
#         return {
#             'out': value
#         }