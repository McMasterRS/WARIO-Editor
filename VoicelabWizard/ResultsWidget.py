from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from VoicelabWizard.DefaultSettings import display_whitelist

import seaborn as sns

import parselmouth

###################################################################################################
# ResultsWidget :
# Wraps the widgets and functionality for displaying results from a single analyzed voice file.
###################################################################################################

class ResultsWidget(QWidget):

    def __init__(self):
        super().__init__()
        
        self.cache = {}
        self.stack = QStackedWidget()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.stack)
        self.setLayout(self.layout)

    def load_results(self, results):
        self.cache = {}
        self.results = results

    def show_result(self, voice_file):

        # Check if these results have already been presented
        if voice_file in self.cache:

            # If they have, switch to the approprate stack item
            index = self.stack.indexOf(self.cache[voice_file])
            self.stack.setCurrentIndex(index)

            # If not, create a new stack item, add it to the stack, and switch to it
        else:
            stack_widget = QWidget()
            stack_layout = QVBoxLayout()
            stack_widget.setLayout(stack_layout)

            figure = self.results['files'][voice_file]['Visualize Voice']['figure']
            
            spectrogram = FigureCanvas(figure)

            tabs = QTabWidget()

            for i, fn_name in enumerate(self.results['files'][voice_file]):
                display_results = {}

                # loop through results, build a list of allowed outputs
                for result_name in self.results['files'][voice_file][fn_name]:
                    result_value = self.results['files'][voice_file][fn_name][result_name]

                    if type(result_value) in display_whitelist:
                        display_results[result_name] = result_value

                n_cols = 1
                n_rows = len(display_results)

                if n_rows > 0:
                    tab = QWidget()
                    tabs.addTab(tab, fn_name)
                    tab_layout = QVBoxLayout()
                    tab.setLayout(tab_layout)
                    table = QTableWidget()
                    tab_layout.addWidget(table)
                    table.setRowCount(n_rows)
                    table.setColumnCount(n_cols)
                    table.setHorizontalHeaderLabels([fn_name])
                    table.setVerticalHeaderLabels(display_results.keys())
                    table.setEditTriggers(QTableWidget.NoEditTriggers)
                    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

                    for j, fn_result in enumerate(display_results):
                        result_value = display_results[fn_result]
                        table.setItem(j,0, QTableWidgetItem(str(result_value)))

            stack_layout.addWidget(spectrogram)
            stack_layout.addWidget(tabs)

            self.stack.addWidget(stack_widget)
            self.cache[voice_file] = stack_widget
            index = self.stack.indexOf(stack_widget)
            self.stack.setCurrentIndex(index)
