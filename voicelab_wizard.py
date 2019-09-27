import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from pipeline.Pipeline import Pipeline
from toolkits.Voicelab.MeasureNode import *
from toolkits.Voicelab.ManipulateNode import *
from toolkits.Voicelab.VisualizeNode import *
from toolkits.Voicelab.IONodes import LoadVoicesNode
from pipeline.QWidgetValueAccesser import QWidgetValueAccesser

from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

import numpy as np
import seaborn as sns


###################################################################################################
###################################################################################################

class SpectrogramDisplay(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Create a figure for the spectrogram
        self.figure_canvas = FigureCanvas(Figure())
        self.layout.addWidget(self.figure_canvas)
        self.fig, self.axis = self.figure_canvas.figure, self.figure_canvas.figure.subplots()

    def draw_spectrogram(self, voice, pitch=None, intensity=None, formants=None):

        self.axis.clear()

        voice = parselmouth.Sound(voice)
        intensity = voice.to_intensity()
        pre_emphasized_voice = voice.copy()
        pre_emphasized_voice.pre_emphasize()
        length_of_window = 0.005
        dynamic_range = 70  # todo put this value in defaults and allow user to specify this value in advanced mode
        spectrogram = pre_emphasized_voice.to_spectrogram(window_length=length_of_window, maximum_frequency=8000)
        x, y = spectrogram.x_grid(), spectrogram.y_grid()


def create_spectrogram(voice, pitch=None, intensity=None, formants=None, settings=None):
    
    fig, axis = plt.subplots()
    voice.pre_emphasize()
    spectrogram = voice.to_spectrogram(window_length=0.005, maximum_frequency=8000)
    x, y = spectrogram.x_grid(), spectrogram.y_grid()

    x_label, y_label = None, None
    colour = None
    return fig, axis

value_accessor = QWidgetValueAccesser()

def measure(feature_settings, file_locations):

    pipeline = Pipeline()
    # Hook up a dumy node to load files into
    load_voices = LoadVoicesNode('Load Voice')
    load_voices.args['file_locations'] = file_locations
    pipeline.add(load_voices)

    # Iterate over each feature to add to the pipeline
    for feature in feature_settings:

        # Only use checked features, can be optimized further using a seperate dictionary of only checked features
        if feature_settings[feature]['checked']:
            node = feature_settings[feature]['node']
            pipeline.add(node)

            # Attach the appropriate arguments to the node
            for option in feature_settings[feature]['options']:
                widget = feature_settings[feature]['options'][option]['widget']
                node.args[option] = value_accessor.get_value(widget)

            # If it doesnt depend on the output of another node just connect it to the root load node
            if 'requires' not in feature_settings[feature]:
                pipeline.connect((load_voices, 'voice'),(node, "voice"))

            # If it does require other nodes, connect to all of those nodes along the appropriate attributes 
            elif 'requires' in feature_settings[feature]:
                for required_feature_name, required_attributes in feature_settings[feature]['requires']:
                    required_feature = feature_settings[required_feature_name]['node']
                    for required_attribute in required_attributes:
                        pipeline.connect((required_feature, required_attribute), (node, required_attribute))

    return pipeline

class FilesTab(QWidget):

    def __init__(self, feature_settings, results, file_locations):

        super().__init__()
        self.feature_settings = feature_settings
        self.file_locations = file_locations
        self.results = results
        self.initUI()

    def initUI(self):

        # FilesTab 
        self.layout = QVBoxLayout()

        # Loaded Voices List
        self.loaded_files = {}
        self.loaded_voices_list = QListWidget()

        self.list_widget = QListWidget()

        # Add Voices Button
        add_voices_btn = QPushButton("Add Sound File")
        remove_voices_btn = QPushButton("Remove Sound File")
        remove_all_btn = QPushButton("Remove All Files")
        automatic_start_btn = QPushButton("Start")

        add_voices_btn.clicked.connect(self.onclick_add)
        remove_voices_btn.clicked.connect(self.onclick_remove)
        automatic_start_btn.clicked.connect(self.onclick_start)

        self.layout.addWidget(add_voices_btn)
        self.layout.addWidget(remove_voices_btn)
        self.layout.addWidget(self.list_widget)
        self.layout.addWidget(automatic_start_btn)

        # Loaded Voice List
        self.setLayout(self.layout)

    def onclick_start(self):

        pipeline = measure(self.feature_settings, self.file_locations)
        self.results['values'] = pipeline.start()
        self.results['changed'] = True

    def onclick_add(self):

        options = QFileDialog.Options()
        temp_loaded = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","Sound Files (*.wav *.mp3)", options=options)[0]
        for loaded in temp_loaded:
            if loaded not in self.file_locations:
                self.file_locations[loaded] = loaded
                QListWidgetItem(parent=self.list_widget).setText(loaded)

    def onclick_remove(self):
        for item in self.list_widget.selectedItems():
            self.list_widget.takeItem(self.list_widget.row(item))

###################################################################################################
###################################################################################################

class SettingsTab(QWidget):

    def __init__(self, feature_settings):

        super().__init__()
        self.feature_settings = feature_settings
        self.initUI()

    def initUI(self):

        self.layout = QVBoxLayout()

        self.is_active = True
        self.advanced_toggle = QCheckBox("Use Advanced Settings")
        self.advanced_toggle.stateChanged.connect(self.toggle_settings)

        self.measure_settings = MeasureSettings(self.feature_settings)
        self.layout.addWidget(self.advanced_toggle)
        self.layout.addWidget(self.measure_settings)
        self.measure_settings.setDisabled(self.is_active)
        self.setLayout(self.layout)
    
    def toggle_settings(self):

        self.is_active = not self.is_active
        self.measure_settings.setDisabled(self.is_active)

###################################################################################################
###################################################################################################

class MeasureSettings(QWidget):

    def __init__(self, feature_settings):

        super().__init__()
        self.feature_settings = feature_settings

        self.measure_layout = QHBoxLayout()
        self.measure_list = QListWidget()
        self.measure_stack = QStackedWidget()

        self.list_items = {}
        self.list_stacks = {}
        self.stack_layouts = {}
        self.leftlist = QListWidget()
        self.stack = QStackedWidget(self)
        
        for feature in self.feature_settings:

            # Add this option to the list with appropriate text and checkbox
            self.list_items[feature] = QListWidgetItem(parent=self.leftlist)
            self.list_items[feature].setText(feature)
            self.list_items[feature].setCheckState(self.feature_settings[feature]['checked'])

            # Add the appropriate configuration widgets
            self.list_stacks[feature] = QWidget()
            self.stack.addWidget(self.list_stacks[feature])
            self.stack_layouts[feature] = QFormLayout()

            for option in self.feature_settings[feature]['options']:
                widget = self.feature_settings[feature]['options'][option]['widget']
                value = str(self.feature_settings[feature]['options'][option]['default_value'])
                value_accessor.set_value(widget, value)
                # value = value_accessor.get_value(widget)
                self.stack_layouts[feature].addRow(option, widget)

            self.list_stacks[feature].setLayout(self.stack_layouts[feature])

        hbox = QHBoxLayout(self)
        hbox.addWidget(self.leftlist)
        hbox.addWidget(self.stack)

        self.setLayout(hbox)
        self.leftlist.currentRowChanged.connect(self.display)
        self.leftlist.itemChanged.connect(self.onchange_check)

    ###############################################################################################

    def onchange_check(self, e):

        if e.checkState() == 2:
            self.feature_settings[e.text()]['checked'] = True
        else:
            self.feature_settings[e.text()]['checked'] = False

    def display(self,i):
        self.stack.setCurrentIndex(i)

###################################################################################################
###################################################################################################

class OutputTab(QWidget):

    def __init__(self, feature_settings, results, file_locations):

        super().__init__()
        self.feature_settings = feature_settings
        self.results = results
        self.file_locations = file_locations

        self.layout = QVBoxLayout()
        result_widget = QLabel()
        result_widget.text = "str(attribute_result)"
        self.layout.addWidget(result_widget)

        self.initUI()

    def initUI(self):

        # Output tab

        self.list_items = {}
        self.list_stacks = {}
        self.stack_layouts = {}
        self.stack_textareas = {}
        self.spectrogram_displays = {}
        self.spectrogram_figures = {}
        self.spectrogram_axis = {}

        self.leftlist = QListWidget()
        self.stack = QStackedWidget(self)
        self.leftlist.currentRowChanged.connect(self.display)

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.leftlist)
        self.layout.addWidget(self.stack)
        self.setLayout(self.layout)

        SpectrogramDisplay().draw_spectrogram('./test_voices/f4047_ah.wav')


        # self.layout.addWidget(self.display_area)

    def display(self,i):
        self.stack.setCurrentIndex(i)

    def update_results_view(self):
        
        file_locations = [location for location in self.file_locations]

        print('Check', self.results['changed'])

        # We only want to update if there are results and those results have changed
        if self.results['changed']:
            print('changed', self.results['values'])

            # We've seen these results, reset to false
            self.results['changed'] = False

            # For each file get its results
            for i, pass_result in enumerate(self.results['values']):
                
                # Create a new layout for this stack
                self.stack_layouts[i] = QVBoxLayout()
                self.list_stacks[i] = QWidget()
                self.list_stacks[i].setLayout(self.stack_layouts[i])

                # Create a new list item for each loaded file
                self.list_items[i] = QListWidgetItem(parent=self.leftlist)
                self.list_items[i].setText(file_locations[i])

                # Create figure canvases for each file
                # create a text area for each loaded file
                self.stack_textareas[i] = QPlainTextEdit()
                self.stack_textareas[i].setReadOnly(True)
                self.stack_layouts[i].addWidget(self.stack_textareas[i])

                # add the stacks to the container stack
                self.stack.addWidget(self.list_stacks[i])

                # For each node get its results
                for run_result_name in pass_result:
                    run_result = pass_result[run_result_name]
                    self.stack_textareas[i].insertPlainText("\n#############################\n"+run_result_name.node_id+"\n#############################\n")

                    # For each attribute on this node get its result
                    for attribute_result_name in run_result:
                        if attribute_result_name == 'voice':
                            voice = parselmouth.Sound(file_locations[i])
                        else:
                            attribute_result = run_result[attribute_result_name]
                            self.stack_textareas[i].insertPlainText("\n@@@@@  "+attribute_result_name+"  @@@@@\n\n")
                            self.stack_textareas[i].insertPlainText(str(attribute_result))

class VoicelabWizard(QWidget):

    def __init__(self):

        super().__init__()
        self.file_locations = {}
        pitch_combo = QComboBox()
        hnr_combo = QComboBox()

        # shared results variable
        self.results = {
            'changed': False,
            'values': {}
        }

        # feature_configuration
        self.feature_settings = {
            'Measure Pitch': {
                'type': 'Measure',
                'checked': True,
                'options': {
                    'Algorithm': {
                        'default_value': 'cc',
                        'widget': pitch_combo
                    },
                    'Time Step': {
                        'default_value': 0,
                        'widget': QLineEdit()
                        },
                    'Max Candidates': {
                        'default_value': 15,
                        'widget': QLineEdit()
                        },
                    'Accuracy': {
                        'default_value': 'no',
                        'widget': QLineEdit()
                        },
                    'Silence Threshold': {
                        'default_value': 0.03,
                        'widget': QLineEdit()
                        },
                    'Voicing Threshold': {
                        'default_value': 0.45,
                        'widget': QLineEdit()
                        },
                    'Octave Cost': {
                        'default_value': 0.01,
                        'widget': QLineEdit()
                        },
                    'Octave Jump Cost': {
                        'default_value': 0.35,
                        'widget': QLineEdit()
                    },
                    'Voiced/Unvoiced Cost': {
                        'default_value': 0.14,
                        'widget': QLineEdit()
                        },
                },
                'node': MeasureVoicePitch("Measure Pitch")
            },
            'Measure Jitter': {
                'type': 'Measure',
                'checked': False,
                'options': {
                    'Floor': {
                        'default_value': 50,
                        'widget': QLineEdit()
                        },
                    'Ceiling': {
                        'default_value': 500,
                        'widget': QLineEdit()
                        },
                    'Start Time': {
                        'default_value': 0,
                        'widget': QLineEdit()
                        },
                    'End Time': {
                        'default_value': 0,
                        'widget': QLineEdit()
                        },
                    'Shortest Period': {
                        'default_value': 0.0001,
                        'widget': QLineEdit()
                        },
                    'Longest Period': {
                        'default_value': 0.02,
                        'widget': QLineEdit()
                        },
                    'Max Period Factor': {
                        'default_value': 1.3,
                        'widget': QLineEdit()
                        },
                },
                'node': MeasureJitter("Measure Jitter") 
            },
            'Measure HNR': {
                'type': 'Measure',
                'checked': False,
                'options': {
                    'Algorithm': {
                        'default_value': 'To Harmonicity (cc)',
                        'widget': hnr_combo
                        },
                    'Floor': {
                        'default_value': 50,
                        'widget': QLineEdit()
                        },
                    'Ceiling': {
                        'default_value': 500,
                        'widget': QLineEdit()
                        },
                    'Time step': {
                        'default_value': 0.01,
                        'widget': QLineEdit()
                        },
                    'Silence threshold': {
                        'default_value': 0.1,
                        'widget': QLineEdit()
                        },
                    'Periods per window': {
                        'default_value': 1.0,
                        'widget': QLineEdit()
                        },
                },
                'node': MeasureHNR("Measure HNR")
            },
            'Measure Duration': {
                'type': 'Measure',
                'checked': False,
                'options': {},
                'node': MeasureVoiceDuration("Measure Duration")
            },
            'Measure Intensity': {
                'type': 'Measure',
                'checked': False,
                'options': {},
                'node': MeasureIntensity("Measure Intensity")
            },
            'Measure Shimmer': {
                'type': 'Measure',
                'checked': False,
                'options': {
                    'floor': {
                        'default_value': 50,
                        'widget': QLineEdit()
                        },
                    'start time': {
                        'default_value': 500,
                        'widget': QLineEdit()
                        },
                    'ceiling': {
                        'default_value': 0,
                        'widget': QLineEdit()
                        },
                    'end time': {
                        'default_value': 0,
                        'widget': QLineEdit()
                        },
                    'shortest period': {
                        'default_value': 0.0001,
                        'widget': QLineEdit()
                        },
                    'longest period': {
                        'default_value': 0.02,
                        'widget': QLineEdit()
                        },
                    'max period factor': {
                        'default_value': 1.3,
                        'widget': QLineEdit()
                        },
                    'max amplitude': {
                        'default_value': 1.6,
                        'widget': QLineEdit()
                        },
                },
                'node': MeasureShimmer("Measure Shimmer")
            },
            'Measure Formants': {
                'type': 'Measure',
                'checked': False,
                'options': {
                    'time step': {
                        'default_value': 0,
                        'widget': QLineEdit()
                        },
                    'max number formants': {
                        'default_value': 5,
                        'widget': QLineEdit()
                        },
                    'max formants': {
                        'default_value': 5500,
                        'widget': QLineEdit()
                        },
                    'window length(s)': {
                        'default_value': 0.025,
                        'widget': QLineEdit()
                        },
                    'preemphasis from': {
                        'default_value': 50,
                        'widget': QLineEdit()
                        },
                    'pitch floor': {
                        'default_value': 50,
                        'widget': QLineEdit()
                        },
                    'pitch ceiling': {
                        'default_value': 500,
                        'widget': QLineEdit()
                        },
                },
                'node': MeasureVoiceFormant("Measure Formants")
            },
            'Measure Vocal Tract': {
                'type': 'Measure',
                'checked': False,
                'options': {},
                'node': MeasureVocalTractEstimates("Measure Vocal Tract"),
                'requires': [('Measure Formants', ['formants'])]
            },
            'Measure Jitter PCA': {
                'type': 'Measure',
                'checked': True,
                'options': {},
                'node': MeasureJitterPCA("Measure Jitter PCA"),
                'requires': [('Measure Jitter', ['local_jitter', 'local_abs_jitter', 'rap_jitter', 'ppq5_jitter', 'ddp_jitter'])]
            },
            'Measure Shimmer PCA': {
                'type': 'Measure',
                'checked': False,
                'options': {},
                'node': MeasureShimmerPCA('Measure Shimmer PCA')
            },
            'Measure Formant PCA': {
                'type': 'Measure',
                'checked': False,
                'options': {},
                'node': MeasureFormantPCA('Measure Formant PCA')
            },
            'Manipulate Pitch': {
                'type': 'Manipulate',
                'checked': False,
                'options': {},
                'node': ManipulatePitchNode('Manipulate Pitch')
            },
            'Manipulate Formant': {
                'type': 'Manipulate',
                'checked': False,
                'options': {},
                'node': ManipulateFormantsNode('Manipulate Formant')
            },
            'Manipulate Pitch and Formant': {
                'type': 'Manipulate',
                'checked': False,
                'options': {},
                'node': ManipulatePitchAndFormants('Manipulate Pitch and Formant')
            },
            'Manipulate Gender and Age': {
                'type': 'Manipulate',
                'checked': False,
                'options': {},
                'node': ManipulateGenderAge('Manipulate Gender and Age')
            },
            'Visualize Spectrogram': {
                'type': 'Visualize',
                'checked': False,
                'options': {
                    'Band Width': {
                        'default_value': 0.05,
                        'widget': QLineEdit()
                    }
                },
                'node': PlotSpectrogram('Visualize Spectrogram')
            },
            'Visualize Pitch': {
                'type': 'Visualize',
                'checked': False,
                'options': {
                    'Pitch Axis': {
                        'default_value': 500,
                        'widget': QLineEdit()
                    }
                },
                'node': PlotPitch('Visualize Pitch')
            },
            'Visualize Intensity': {
                'type': 'Visualize',
                'checked': False,
                'options': {},
                'node': PlotIntensity('Visualize Intensity')
            },
            'Visualize Formants': {
                'type': 'Visualize',
                'checked': False,
                'options': {},
                'node': PlotFormants('Visualize Formants')
            }
        }
        pitch_algorithms = ['To Pitch (cc)', 'To Pitch (ac)']
        for algorithm in pitch_algorithms:
                pitch_combo.addItem(algorithm)

        # cross-correlation (cc) and auto-correlation (ac) methods
        hnr_algorithms = ['To Harmonicity (cc)', 'To Harmonicity (ac)']
        for algorithm in hnr_algorithms:
            hnr_combo.addItem(algorithm)

        self.initUI()
        self.show()

    def initUI(self):

        self.setWindowTitle("Voicelab")
        self.setGeometry(500,500,500,500)
        self.setWindowTitle('VOICELAB')
        self.layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.file_tab = FilesTab(self.feature_settings, self.results, self.file_locations)
        self.settings_tab = SettingsTab(self.feature_settings)
        self.output_tab = OutputTab(self.feature_settings,  self.results, self.file_locations)

        self.tabs.currentChanged.connect(self.output_tab.update_results_view)

        self.tabs.addTab(self.file_tab, "Input")
        self.tabs.addTab(self.output_tab, "Output")
        self.tabs.addTab(self.settings_tab, "Settings")

        self.tabs.resize(500,500)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        self.show()

if __name__ == "__main__":
    # beginner_measure(pipeline)

    app = QApplication(sys.argv)
    wizard = VoicelabWizard()
    sys.exit(app.exec_())

# takes a pitch object and converts it into the approprate presentation elements
class DisplaySoundWidget(QWidget):
    def __init__(self, pitch):
        super().__init__()
        self.initUI(pitch)

    def initUI(self, pitch):
        self.layout = QHBoxLayout()
        label = QLabel(self.layout)
        label.text = "helloworld"
        self.setLayout(self.layout)

class DisplayPitchWidget(QWidget):
    def __init__(self):
        super().__init__()

    def initUI(self):
        pass

class DisplayIntensityWidget(QWidget):
    def __init__(self):
        super().__init__()

    def initUI(self):
        pass

class DisplayDurationWidget(QWidget):
    def __init__(self):
        super().__init__()
    def initUI(self):
        pass

class DisplayHNRWidget(QWidget):
    def __init__(self):
        super().__init__()

    def initUI(self):
        pass

class DisplayJitterWidget(QWidget):
    def __init__(self):
        super().__init__()

    def initUI(self):
        pass

class DisplayShimmerWidget(QWidget):
    def __init__(self):
        super().__init__()

    def initUI(self):
        pass

class DisplayFormantsWidget(QWidget):
    def __init__(self):
        super().__init__()

    def initUI(self):
        pass

class ResultsView(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        pass
