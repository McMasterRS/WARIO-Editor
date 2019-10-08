import parselmouth
from pipeline.Node import Node
from parselmouth.praat import call
from pipeline.FileWidget import FileWidget

###################################################################################################
# LOAD VOICES NODE
# WARIO pipeline node for loading voice files.
###################################################################################################
# ARGUMENTS
# 'file_locations'   : list of filesystem locations for where to find the voice files
###################################################################################################
# RETURNS
# 'voice' [batch]   : return a parselmouth voice object for each file loaded
###################################################################################################

class LoadVoicesNode(Node):

    def __init__(self, name):
        super().__init__(name)
        self.done = False

    ###############################################################################################
    # process: Retrieve the next file location and return it
    ###############################################################################################
    def process(self):
        item = self.get_next(self.state['voices'])
        return {
            'voice': item
        }

    ###############################################################################################
    # start: WARIO hook, run before any data is processed to load the data in
    ###############################################################################################
    def start(self):
        self.state['voices'] = []

        # If a collection of file locations are present use those, otherwise prompt for them
        if len(self.args['file_locations']) == 0:
            ex = FileWidget()
            self.state['files'] = ex.openFileNamesDialog()
        else:
            self.state['files'] = self.args['file_locations']

        for file_path in self.state['files']:
            self.state['voices'].append(parselmouth.Sound(file_path))
            
    ###############################################################################################
    # get_next: Retrieve the next file location by simply poping off the stack
    ###############################################################################################
    def get_next(self, collection):
        item = collection.pop()
        if len(collection) <= 0:
            self.done = True
        return item