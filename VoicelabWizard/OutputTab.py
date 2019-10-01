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
        results = self.model['results']

        # Create a column layout
        layout = QHBoxLayout()
        self.setLayout(layout)

        # list of voice files that were processed
        self.file_list = QListWidget()
        self.file_list.itemSelectionChanged.connect(self.on_list_change)
        layout.addWidget(self.file_list)

        # presentation widget for the results of processing the voices
        self.results_widget = ResultsWidget()
        layout.addWidget(self.results_widget)

        self.save_button = QPushButton()
        self.save_button.clicked.connect(self.on_save)
        layout.addWidget(self.save_button)

        # create the callback for updating the list with new results
        self.model['update results'] = self.update_results

    def update_results(self, results):

        # reset the file list and results table from previous runs
        self.file_list.clear()

        # Reset the stack of widgets for presenting results
        self.stack = QStackedWidget()

        voice_files = self.model['files']
        results = self.model['results']

        for i, voice_file in enumerate(results):

            # fill the list with paths to the loaded voice files
            list_item = QListWidgetItem(parent=self.file_list)
            list_item.setText(voice_file)
            self.results_widget.load_results(results)
                
    def on_list_change(self):
        selected = self.file_list.selectedItems()

        if len(selected) > 0:
            file_name = selected[0].text()
            self.results_widget.show_result(file_name)
        
    def on_save(self):
        print('saved')

        sheets = {}
        results = self.model['results']
        files = self.model['files']
        functions = self.model['functions']

        sheets = {}

        n_rows = len(files)

        for i, run in enumerate(results):
            file_name = files[i].split('/')[-1].split('.wav')[0]

            for j, fn in enumerate(results[run]):

                if fn not in sheets:

                    sheets[fn] = {}
                    sheets[fn]['file name'] = [None] * n_rows

                sheets[fn]['file name'][i] = files[i]

                for k, result in enumerate(results[run][fn]):

                    result_value = results[run][fn][result]

                    if result not in sheets[fn]:
                        sheets[fn][result] = [None] * n_rows

                    if isinstance(result_value, parselmouth.Sound): # if the result is a sound file, that is probably a manipulate node, save a seperate wav file
                        save_file_name = file_name + '_' + fn.lower() + '.wav'
                        print(save_file_name)
                        result_value.save(save_file_name, 'WAV')
                    
                    sheets[fn][result][i] = result_value

        writer = ExcelWriter('voicelab_results.xlsx')

        for sheet_data in sheets:
            sheet = pd.DataFrame(sheets[sheet_data])
            sheet.to_excel(writer, sheet_data, index=False)

        writer.save()