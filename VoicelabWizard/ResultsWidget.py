from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import seaborn as sns
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
        self.results = results

        # Generate the stack of results presentation widgets
        # for voice_file in results:
        #     for fn_name in results[voice_file]:
        #         for fn_result in results[voice_file][fn_name]:
        #             print(fn_result)
    


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

                n_rows = 1
                n_cols = len(self.results['files'][voice_file][fn_name])

                tab = QWidget()
                tabs.addTab(tab, fn_name)
                tab_layout = QVBoxLayout()
                tab.setLayout(tab_layout)

                table = QTableWidget()
                tab_layout.addWidget(table)
                # set row count
                table.setRowCount(n_cols)

                # set column count
                table.setColumnCount(n_rows)

                table.setHorizontalHeaderLabels([fn_name])
                table.setVerticalHeaderLabels(self.results['files'][voice_file][fn_name].keys())
                table.setEditTriggers(QTableWidget.NoEditTriggers)
                table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

                for j, fn_result in enumerate(self.results['files'][voice_file][fn_name]):
                    table.setItem(j,0, QTableWidgetItem(str(self.results['files'][voice_file][fn_name][fn_result])))

            stack_layout.addWidget(spectrogram)
            stack_layout.addWidget(tabs)

            self.stack.addWidget(stack_widget)
            self.cache[voice_file] = stack_widget
            index = self.stack.indexOf(stack_widget)
            self.stack.setCurrentIndex(index)
