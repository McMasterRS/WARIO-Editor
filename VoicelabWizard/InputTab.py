from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from pipeline.Pipeline import Pipeline
from toolkits.Voicelab.MeasureNode import *
from toolkits.Voicelab.ManipulateNode import *
from toolkits.Voicelab.VisualizeNode import *
from toolkits.Voicelab.IONodes import LoadVoicesNode

class InputTab(QWidget):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.model = self.parent().model

        self.initUI()

    def initUI(self):

        # FilesTab 
        self.layout = QVBoxLayout()

        # List of loaded voice files
        self.list_loaded_voices = QListWidget()

        # Add Voices Button
        btn_add_voices = QPushButton("Add Sound File")
        btn_remove_voices = QPushButton("Remove Sound File")
        btn_start = QPushButton("Start")

        btn_add_voices.clicked.connect(self.onclick_add)
        btn_remove_voices.clicked.connect(self.onclick_remove)
        btn_start.clicked.connect(self.onclick_start)

        self.layout.addWidget(btn_add_voices)
        self.layout.addWidget(btn_remove_voices)
        self.layout.addWidget(self.list_loaded_voices)
        self.layout.addWidget(btn_start)

        # Loaded Voice List
        self.setLayout(self.layout)

    def onclick_add(self):
        options = QFileDialog.Options()
        temp_loaded = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","Sound Files (*.wav *.mp3)", options=options)[0]
        for loaded in temp_loaded:
            if loaded not in self.model['files']:
                self.model['files'].append(loaded)
                QListWidgetItem(parent=self.list_loaded_voices).setText(loaded)

    def onclick_remove(self):
        for item in self.list_loaded_voices.selectedItems():
            self.model['files'].pop(self.model['files'].index(item.text()))
            self.list_loaded_voices.takeItem(self.list_loaded_voices.row(item))

    def onclick_start(self):
        pipeline = self.create_pipeline()
        pipeline_results = pipeline.start()

        # Turn the pipeline results into a more convenient format
        for i, run in enumerate(pipeline_results):
            voice_file = self.model['files'][i]
            self.model['results'][voice_file] = {}

            for node in run:
                node_name = node.node_id
                if node_name != 'Load Voice':
                    self.model['results'][voice_file][node_name] = {}

                    for result in run[node]:
                        self.model['results'][voice_file][node_name][result] = run[node][result]

        self.model['update results'](self.model['results'])

    def create_pipeline(self):
        functions = self.model['functions']
        file_locations = self.model['files']
        pipeline = Pipeline()

        # Create a node that will load all of the voices
        load_voices = LoadVoicesNode('Load Voice')
        # Set up the load node with the appropriate file locations
        load_voices.args['file_locations'] = file_locations
        # add the node to the pipeline
        pipeline.add(load_voices)

        # Create a node that will draw the default spectrogram for the loaded voices, we always want to plot the spectrogram
        visualize_voices = VisualizeVoiceNode('Visualize Voice')
        # Connect the loaded voice to the visualize node
        pipeline.connect((load_voices, 'voice'), (visualize_voices, 'voice'))
        # Add the node to the pipeline
        pipeline.add(visualize_voices)

        # for each checked operation we create the appropriate node, assign its
        # associated parameters, and add it to the pipeline connecting it either 
        # directly to the load node or to its specified parent node
        for fn in functions:
            if self.model['functions'][fn]['checked']:
                pipeline.add(self.model['functions'][fn]['node'])
                parameters = self.model['functions'][fn]['parameters']
                for parameter in parameters:
                    self.model['functions'][fn]['node'].args[parameter.lower()] = parameters[parameter]
                pipeline.connect((load_voices, 'voice'), (self.model['functions'][fn]['node'], 'voice'))

        return pipeline