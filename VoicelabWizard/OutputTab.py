from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import seaborn as sns

import numpy as np
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile

import parselmouth
from parselmouth.praat import call

from VoicelabWizard.ResultsWidget import ResultsWidget

class OutputTab(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        # Model contains the state of data within the program
        self.model = self.parent().model
        # create the callback for updating the list with new results
        self.model['update results'] = self.update_results

        # Create a column layout

        layout = QVBoxLayout()
        self.setLayout(layout)

        results_container = QWidget()
        results_layout = QHBoxLayout()

        # list of voice files that were processed
        self.file_list = QListWidget()
        self.file_list.itemSelectionChanged.connect(self.on_list_change)

        # presentation widget for the results of processing the voices

        results_container.setLayout(results_layout)
        self.results_widget = ResultsWidget()
        self.save_button = QPushButton("Save Results")
        self.save_button.clicked.connect(self.on_save)

        layout.addWidget(results_container)
        layout.addWidget(self.save_button)

        results_layout.addWidget(self.file_list)
        results_layout.addWidget(self.results_widget)


    def update_results(self, results):

        # reset the file list and results table from previous runs
        self.file_list.clear()

        # Reset the stack of widgets for presenting results
        self.stack = QStackedWidget()

        voice_files = self.model['files']
        # results = self.model['results']

        for i, voice_file in enumerate(results['files']):

            # fill the list with paths to the loaded voice files
            list_item = QListWidgetItem(parent=self.file_list)
            list_item.setText(voice_file)
            self.results_widget.load_results(results)

        self.results_widget.show_result(voice_files[0])

    def on_list_change(self):
        selected = self.file_list.selectedItems()

        if len(selected) > 0:
            file_name = selected[0].text()
            self.results_widget.show_result(file_name)
        
    def on_save(self):
        print('saved')

        options = QFileDialog.Options()
        temp_loaded = QFileDialog.getExistingDirectory (self)

        if temp_loaded != '':

            sheets = {}
            results = self.model['results']

            sheets = {}

            for i, fn in enumerate(results['functions']):
                sheets[fn] = {
                    'file name': []
                }
                for j, file_path in enumerate(results['functions'][fn]):
                    sheets[fn]['file name'].append(file_path)
                    file_name = file_path.split('/')[-1].split('.wav')[0]

                    for j, result in enumerate(results['functions'][fn][file_path]):
                        result_value = results['functions'][fn][file_path][result]

                        if isinstance(result_value, parselmouth.Sound):
                            modified_path = temp_loaded + '/' + file_name + '_' + fn.lower().replace(' ', '_') + '.wav'
                            self.save_voice(result_value, modified_path)

                        elif isinstance(result_value, Figure):
                            modified_path = temp_loaded + '/' + file_name + '.png'
                            self.save_spectrogram(result_value, modified_path)

                        else:
                            if result not in sheets[fn]:
                                sheets[fn][result] = []
                            sheets[fn][result].append(str(results['functions'][fn][file_path][result]))

                print(sheets)

            writer = ExcelWriter('voicelab_results.xlsx')

            for sheet_data in sheets:
                sheet = pd.DataFrame(sheets[sheet_data])
                sheet.to_excel(writer, sheet_data, index=False)

            writer.save()


    def save_voice(self, voice, file_name):
        
        voice.save(file_name, 'WAV')
        return file_name
    
    def save_spectrogram(self, spectrogram, file_name):

        spectrogram.savefig(file_name)
        return file_name