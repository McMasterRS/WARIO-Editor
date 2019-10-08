from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import matplotlib.pyplot as plt

from pipeline.Pipeline import Pipeline
# from toolkits.Voicelab.MeasureNode import *
# from toolkits.Voicelab.ManipulateNode import *
# from toolkits.Voicelab.VisualizeNode import *
# from toolkits.Voicelab.IONodes import LoadVoicesNode

import toolkits.Voicelab as Voicelab

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

        # Create and connect add button
        btn_add_voices = QPushButton("Add Sound File")
        btn_add_voices.clicked.connect(self.onclick_add)

        # Create and connect remove button
        btn_remove_voices = QPushButton("Remove Sound File")
        btn_remove_voices.clicked.connect(self.onclick_remove)

        # Create and connect start button
        self.btn_start = QPushButton("Start")
        self.btn_start.clicked.connect(self.onclick_start)
        self.btn_start.setDisabled(True)

        # self.progress = QProgressBar()

        # Display the widgets in the correct order
        self.layout.addWidget(btn_add_voices)
        self.layout.addWidget(btn_remove_voices)
        self.layout.addWidget(self.list_loaded_voices)
        self.layout.addWidget(self.btn_start)
        # self.layout.addWidget(self.progress)

        # Loaded Voice List
        self.setLayout(self.layout)

    def onclick_add(self):
        # Select a collection of voice files using the systems default dialog
        options = QFileDialog.Options()
        temp_loaded = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","Sound Files (*.wav *.mp3)", options=options)[0]

        # Display the loaded files in a list. Only add if the file is not already loaded
        for loaded in temp_loaded:
            if loaded not in self.model['files']:
                self.model['files'].append(loaded)
                QListWidgetItem(parent=self.list_loaded_voices).setText(loaded)

        if len(self.model['files']) > 0:
            self.btn_start.setDisabled(False)

    ###############################################################################################
    # onclick_remove()
    # Remove the all of the selected voice files from the list gui and the data model
    ###############################################################################################
    def onclick_remove(self):
        for item in self.list_loaded_voices.selectedItems():
            self.model['files'].pop(self.model['files'].index(item.text()))
            self.list_loaded_voices.takeItem(self.list_loaded_voices.row(item))

        if len(self.model['files']) == 0:
            self.btn_start.setDisabled(True)

    ###############################################################################################
    # onclick_start()
    # Constructs and starts a WARIO pipeline to process loaded voices according to the settings
    ###############################################################################################
    def onclick_start(self):


        # Create a pipeline reflecting the user's settings
        pipeline = self.create_pipeline(self.model['files'], self.model['functions'])
        pipeline_results = pipeline.start()

        self.model['results'] = {}

        # Index our results by file path, then function name, then results
        for i, run in enumerate(pipeline_results):
            file_path = self.model['files'][i]
            self.model['results'][file_path] = {}

            for j, fn_node in enumerate(run):
                fn_name = fn_node.node_id
                self.model['results'][file_path][fn_name] = run[fn_node]

        # active_functions = ['Visualize Voice']
        # for fn in self.model['functions']:
        #     if self.model['settings'][fn]['checked'] == Qt.PartiallyChecked or self.model['settings'][fn]['checked'] == Qt.Checked:
        #         active_functions.append(fn)

        # self.model['results']['files'] = {key: {} for key in self.model['files']}
        # self.model['results']['functions'] = {key: {} for key in active_functions }

        # # Turn the pipeline results into a more convenient format
        # for i, run in enumerate(pipeline_results):
        #     voice_file = self.model['files'][i]
        #     self.model['results']['files'][voice_file] = {}

        #     for node in run:
        #         node_name = node.node_id

        #         if node_name != 'Load Voice':
        #             self.model['results']['files'][voice_file][node_name] = {}
        #             self.model['results']['functions'][node_name][voice_file] = {}

        #             for result in run[node]:
        #                 self.model['results']['files'][voice_file][node_name][result] = run[node][result]
        #                 self.model['results']['functions'][node_name][voice_file][result] = run[node][result]

        # This is a basic callback function, once the results are finished we want to trigger an
        # update on the results tab
        self.model['update results'](self.model['results'])


    ###############################################################################################
    # create_pipeline: create the approprate WARIO pipeline based on the current settings
    ###############################################################################################
    def create_pipeline(self, file_locations, functions):

        # Empty WARIO pipeline
        pipeline = Pipeline()

        # Create a node that will load all of the voices
        load_voices = Voicelab.LoadVoicesNode('Load Voice')

        # Set up the load node with the appropriate file locations
        load_voices.args['file_locations'] = file_locations

        # Add the node to the pipeline
        pipeline.add(load_voices)

        # Create a node that will draw the default spectrogram for the loaded voices, we always want to plot the spectrogram
        visualize_voices = Voicelab.VisualizeVoiceNode('Visualize Voice')

        # if there are settings the user has configured, we want to attach them to the node
        for value in self.model['settings']['Visualize Voice']['value']:
            visualize_voices.args[value] = self.model['settings']['Visualize Voice']['value'][value]

        # Connect the loaded voice to the visualize node so it has access to it
        pipeline.connect((load_voices, 'voice'), (visualize_voices, 'voice'))

        # Add the node to the pipeline
        pipeline.add(visualize_voices)

        # For each checked operation we create the appropriate node, assign its associated
        # parameters, and add it to the pipeline connecting it to the load voice node and
        # visualize node. those two functions are always performed
        for fn in functions:

            # We only want the checked functions
            if self.model['settings'][fn]['checked'] and fn != 'Visualize Voice':

                # Attach the approprate user settings to each node
                for param in self.model['settings'][fn]['value']:
                    self.model['functions'][fn]['node'].args[param] = self.model['settings'][fn]['value'][param]

                pipeline.add(self.model['functions'][fn]['node'])
                pipeline.connect((load_voices, 'voice'), (self.model['functions'][fn]['node'], 'voice'))
                pipeline.connect((visualize_voices, 'figure'), (self.model['functions'][fn]['node'], 'figure'))

        return pipeline