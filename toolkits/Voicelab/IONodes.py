import parselmouth
from pipeline.Node import Node
from parselmouth.praat import call
from pipeline.FileWidget import FileWidget

class LoadVoiceNode(Node):
    def process(self):
        voice_file = self.args['voice_file']
        voice = parselmouth.Sound(voice_file)

        print('voice')
        print(voice)
        
        return {'voice': voice}

class LoadVoicesNode(Node):
    '<- files, -> voice'
    def __init__(self, name):
        super().__init__(name)
        self.done = False

    def process(self):
        item = self.get_next(self.state['voices'])
        return {
            'voice': item
        }

    def start(self):
        self.state['voices'] = []

        # You can optionally pass in file locations otherwise it will prompt for files
        if len(self.args['file_locations']) == 0:
            ex = FileWidget()
            self.state['files'] = ex.openFileNamesDialog()
        else:
            self.state['files'] = self.args['file_locations']

        for file_path in self.state['files']:
            self.state['voices'].append(parselmouth.Sound(file_path))

    def get_next(self, collection):
        item = collection.pop()
        if len(collection) <= 0:
            self.done = True
        return item