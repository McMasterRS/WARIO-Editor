###################################################################################################
# Node/Task
# + Abstract node for handling the running of a discrete task in a workflow
###################################################################################################

class Node():
    """ abstract node class. this describes a single operational function in our process pipeline """

    upstream = {}
    downstream = {}
    signature = {}
    delay = False
    children = {}
    edges = {}
    ready = False

    def __init__(self, name):
        self.name = name

    # ready state is calulated by logically AND'ing the signature
        
    def process(self, *args, **kwargs):
        results = {}
        return results

    def send(self, parent_attribute, result):
        child, child_attribute = self.downstream[parent_attribute]
        print("child: ", child, child_attribute)
        child.upstream[child_attribute] = result
        print("child: ", child, child_attribute)
        child.signature[child_attribute] = True # we want the child to know there is data waiting for it on that edge


###################################################################################################
# DelayedNode/DelayedTask:: Node
# + A node collects it's incoming data until it is ready.
###################################################################################################

class DelayedNode(Node): # BatchedNode

    state = {} # State as maintained accross some set of runs or batches.
    delay = True

    def _reset(self):
        self.state = {}

    def _process(self, *args, **kwargs):
        self.state = self._resolve_state(self.state, *args, **kwargs)
        self.process(**self.state)

    def _resolve_state(self, state, *args, **kwargs):
        return state

###################################################################################################
# InitializationNode:: Node
# + A Node which performs an operation before the pipeline is constructed.
###################################################################################################

class InitializationNode(Node): # InputNode
    """ Node:: Performs an operation before the pipeline is constructed """

###################################################################################################
#
###################################################################################################

class InputNode(Node):
    """ this is a type of Node that inputs things and sends partial data periodically as a batch of runs """

    batch = []  # The complete set of data for a process to run. A directory of one or more files.
    run = [] # A subset of a batch, a set of rows in a file for example
    row = [] # A subset of a run, an single row in a file for example

    batch_finished = False
    run_finished = False
    row_finished = False
    ready = False

    def load_batch(self):
        return [[[]]]

    # this is part of the running code, it consumes the next piece of data, then pushes it onwards
    def _process(self):
        value = None

        # This is the process of iterating through and populating the batch, run, and row data
        if len(self.row) == 0: # this is the last one in the row
            self.row_finished = True
            if len(self.run) == 0: # this is the last one in the run
                self.run_finished = True
                if len(self.batch) == 0: # this is the last one in the batch
                    self.batch_finished = True
                else: # there is still some left in the batch
                    self.run = self.batch.pop()
                    self.row = self.run.pop()
                    self.value = self.row.pop()
                    self.run_finished = False
                    self.row_finished = False
            else: # there is still som left in the run
                self.row = self.run.pop()
                self.value = self.row.pop()
                self.row_finished = False
        else:
            value = self.row.pop() # we wouldnt be running this if there was nothing in the row

        # print(self.row)

        return {
            "out": value
        }

###################################################################################################
#
###################################################################################################

class OutputNode(Node):
    """ abstract node with no children, this is used to output the results of the process """
    
    def finish_batch(self, batch):
        """ concludes the running of a batch of runs """
    
    def finish_run(self, run, batch):
        """ concludes the running of a run """

    def output_after_batch(self, batch):
        return batch

    def output_after_run(self, run):
        return run

import csv
###################################################################################################
#
###################################################################################################

class FileInputNode(InputNode):
    """ This is an input node where each item is a row of a file or each row in a set of files. """ 

    def load_batch(self, batch=[]):
        """ load the data for the whole batch, in this case, a set of files """ 

        file_locations = self.prompt_file_locations()
        for location in file_locations:
            batch.append(self.read_file(location))

        return batch

    def prompt_file_locations(self):
        """ prompt the user with a graphical file selector """
        
        file_locations = ["./test1.csv", "test2.csv"]

        return file_locations

    def read_file(self, file_location):
        """ reads all of the data from a set of file locations. returns the raw data """

        data = []

        with open(file_location) as f:
            data = list(csv.reader(f))

        return data

###################################################################################################
#
###################################################################################################

class ConsoleInputNode(InputNode):
    """ this is an input node where each item is recieved from user input on the command line """

    def input_prompt(self):
        """ prompt the user with instructions on the command line """

import random

###################################################################################################
#
###################################################################################################

class RandomInputNode(InputNode):
    """ fills a set of columns and rows with random numbers and pushes them as a batch and runs """

    def __init__(self, n_rows=0, n_columns=0, rand_min=0, rand_max=1, precision=3):
        self.n_rows = n_rows
        self.n_columns = n_columns
        self.rand_min = rand_min
        self.rand_max = rand_max
        self.precision = precision

    def load_batch(self, batch=[]):
        batch = [[random.randrange(self.rand_min, self.rand_max) for i in range(self.n_columns)] for j in range(self.n_rows)]
        return batch

    def load_next_run(self, batch):
        run = batch.pop()
        return run, batch

###################################################################################################
#
###################################################################################################

class FileRunOutputNode(OutputNode):
    def output_after_run(self, run, output_file=None):
        pass

###################################################################################################
#
###################################################################################################

class FileBatchOutputNode(OutputNode):
    def output_after_batch(self, run, output_file=None):
        pass

###################################################################################################
#
###################################################################################################

class PlotBatchOutputNode(OutputNode):
    def output_after_batch(self, batch, x_axes=None, y_axes=None ):
        pass

###################################################################################################
#
###################################################################################################

class PlotRunOutputNode(OutputNode):
    def output_after_run(self, run, x_axes=None, y_axes=None ):
        pass

###################################################################################################
#
###################################################################################################

class ConsoleOutputNode(OutputNode):
    def output_after_run(self, run):
        pass

###################################################################################################
#
###################################################################################################
class PrintNode(Node):

    def _process(self, value):
        print("PRINTNODE: ", value)
        return {
            'out': value
        }