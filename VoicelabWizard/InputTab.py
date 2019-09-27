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
            if loaded not in self.model['loaded files']:
                self.model['loaded files'].append(loaded)
                QListWidgetItem(parent=self.list_loaded_voices).setText(loaded)

    def onclick_remove(self):
        for item in self.list_loaded_voices.selectedItems():
            self.model['loaded files'].pop(self.model['loaded files'].index(item.text()))
            self.list_loaded_voices.takeItem(self.list_loaded_voices.row(item))

    def onclick_start(self):
        pipeline = self.create_pipeline()
        self.results['values'] = pipeline.start()
        self.results['changed'] = True

    def create_pipeline(self):
        pipeline = Pipeline()

        # Create a node to load voices into
        load_voices = LoadVoicesNode('Load Voice')
        load_voices.args['file_locations'] = file_locations
        pipeline.add(load_voices)