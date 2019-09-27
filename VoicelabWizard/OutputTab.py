from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import seaborn as sns

import numpy as np
import pandas as pd

import parselmouth
from parselmouth.praat import call

class SpectrogramDisplay(QWidget):

    def __init__(self):
        super().__init__()
        self.canvas = FigureCanvas(Figure())
        self.axis = self.canvas.figure.subplots()
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def draw_spectrogram(self, voice, pitch=None, intensity=None, formants=None):
        length_of_window = 0.05
        dynamic_range = 70 

        pre_emphasized_voice = voice.copy()
        pre_emphasized_voice.pre_emphasize()
        spectrogram = pre_emphasized_voice.to_spectrogram(window_length=length_of_window, maximum_frequency=8000)
        x, y = spectrogram.x_grid(), spectrogram.y_grid()

        sg_db = 10 * np.log10(spectrogram.values)
        vgmin_value = sg_db.max() - dynamic_range
        self.axis.pcolormesh(x, y, sg_db, vmin=vgmin_value, cmap='binary')

        self.axis.set_ylim([spectrogram.ymin, spectrogram.ymax])
        self.axis.set_xlabel("Time [s]", labelpad=15)
        self.axis.set_ylabel("Frequency [Hz]", labelpad=15)
        self.axis.set_xlim([voice.xmin, voice.xmax])
        sns.set()

        if pitch is not None:
            pitch_axis = self.axis.twinx()
            intensity = voice.to_intensity()
            pitch_values = pitch.selected_array['frequency']
            sample_times = pitch.xs()
            for i, time in enumerate(sample_times):
                intensity.values.T[intensity.values.T < 50] = np.nan
                intensity_value = call(intensity, "Get value at time", time, "cubic")
                if intensity_value < 50:
                    pitch_values[i] = 0

            pitch_values[pitch_values == 0] = np.nan
            pitch_axis.plot(pitch.xs(), pitch_values, linestyle='-', color='k', linewidth=6)
            pitch_axis.plot(pitch.xs(), pitch_values, linestyle='-', color='w', linewidth=5)
            pitch_axis.plot(pitch.xs(), pitch_values, linestyle='-', color='b', linewidth=4)
            pitch_axis.grid(False)

            mode = 'automatic'
            if mode == 'advanced':
                # todo get this value from user
                pass
            else:  # automatic, basic, and intermediate modes
                pitch_lim = 500

            pitch_axis.set_ylim(0, pitch_lim)
            pitch_axis.set_ylabel("Fundamental frequency [Hz]")
            pitch_axis.yaxis.label.set_color('b')

        if intensity is not None:
            intensity_axis = self.axis.twinx()
            intensity.values.T[intensity.values.T < 50] = np.nan
            intensity_axis.plot(intensity.xs(), intensity.values.T, linewidth=3, color='k')
            intensity_axis.plot(intensity.xs(), intensity.values.T, linewidth=2, color='w')
            intensity_axis.plot(intensity.xs(), intensity.values.T, linewidth=1, color='g')
            intensity_axis.grid(False)
            plt.ylim(50)
            intensity_axis.set_ylabel("Intensity [dB]")
            intensity_axis.yaxis.label.set_color('g')

        if formants is not None:
            pass

class OutputTab(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.model = self.parent().model

        voice = parselmouth.Sound('./test_voices/f4047_ah.wav')
        pitch = call(voice, "To Pitch (cc)", 0, 50, 15, "yes", 0.03, 0.45, 0.01, 0.35, 0.14, 500)

        layout = QHBoxLayout()
        column_widgets = [QWidget() for i in range(2)]
        column_layouts = [QVBoxLayout() for i in range(2) ]

        for i in range(len(column_widgets)):
            column_widgets[i].setLayout(column_layouts[i])
            layout.addWidget(column_widgets[i])

        self.list_area = QListWidget()
        self.list_area.currentRowChanged.connect(self.on_list_change)

        save_button = QPushButton()
        save_button.setText('Save Results')
        save_button.clicked.connect(self.on_save)
        
        spectrogram_display = SpectrogramDisplay()
        spectrogram_display.draw_spectrogram(voice, pitch=pitch)

        self.text_area = QPlainTextEdit()
        self.text_area.setReadOnly(True)

        column_widgets[0].layout().addWidget(self.list_area)
        column_widgets[0].layout().addWidget(save_button)
        column_widgets[1].layout().addWidget(spectrogram_display)
        column_widgets[1].layout().addWidget(self.text_area)

        self.setLayout(layout)
        self.update_results(['a', 'b', 'c'], {
            'a': 'a',
            'b' : 'b'
        })

    def update_results(self, voice_files, results):

        self.list_area.clear()
        self.text_area.clear()

        for voice_file in voice_files:
            list_items = QListWidgetItem(parent=self.list_area)
            list_items.setText(voice_file)

        for result in results:
            self.text_area.insertPlainText(result + ' = ' + results[result] + '\n')

    def on_list_change(self):
        print('change')
        
    def on_save(self):
        print('saved')