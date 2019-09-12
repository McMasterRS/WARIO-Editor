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


###################################################################################################
###################################################################################################

value_accessor = QWidgetValueAccesser()

def measure(feature_settings=None, file_locations=[]):

    pipeline = Pipeline()
    load_voices = LoadVoicesNode('')
    load_voices.args['file_locations'] = file_locations
    pipeline.add(load_voices)
    feature_settings = {}

    for feature in feature_settings:
        if feature_settings[feature]['checked']:
            feature_settings[feature] = {}
            for option in feature_settings[feature]['options']:
                widget = feature_settings[feature]['options'][option]['widget']
                feature_settings[feature][option] = value_accessor.get_value(widget)

    # Automatically measure all features, this is the default if no params are specified
    if not any(feature_settings):
        for feature in feature_settings:
            pipeline.add(feature_settings[feature]['node'])
            pipeline.connect((load_voices, 'voice'),(feature_settings[feature]['node'], "voice"))

    # Measure only the features specified, and optionally adjust their algorithms and input params
    else:
        for feature in feature_settings:
            for option in feature_settings[feature]:
                feature_settings[feature]['node'].args[option] = feature_settings[feature][option]
            pipeline.add(feature_settings[feature]['node'])
            pipeline.connect((load_voices, 'voice'),(feature_settings[feature]['node'], "voice"))

    return pipeline

def visualize(feature_settings=None, pipeline=None):
    nodes = pipeline.nodes
    # for node in nodes:
    #     pipeline.connect(node, )
    return pipeline

class FilesTab(QWidget):

    def __init__(self, feature_settings):
        super().__init__()
        self.feature_settings = feature_settings
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
        # print(self.feature_settings)
        file_locations = [str(self.list_widget.item(i).text()) for i in range(self.list_widget.count())]
        pipeline = measure(feature_settings=self.feature_settings, file_locations=file_locations)
        pipeline = visualize(feature_settings=self.feature_settings, pipeline=pipeline)
        results = pipeline.start()
        print(results)

    def onclick_add(self):
        options = QFileDialog.Options()
        self.file_locations = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","Sound Files (*.wav *.mp3)", options=options)
        for i, self.file_location in enumerate(self.file_locations[0]):
            QListWidgetItem(parent=self.list_widget).setText(self.file_location)

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

    # def click_handler(self, stack):
    #     pipeline = measure(feature_settings)
    #     pipeline.start()

    def display(self,i):
        self.stack.setCurrentIndex(i)

###################################################################################################
###################################################################################################

class OutputTab(QWidget):

    def __init__(self, feature_settings):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        static_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(static_canvas)

        self._static_ax = static_canvas.figure.subplots()
        t = np.linspace(0, 10, 501)
        self._static_ax.plot(t, np.tan(t), ".")
        self.setLayout(layout)
        
class VoicelabWizard(QWidget):

    def __init__(self):
        super().__init__()

        self.file_locations = []

        pitch_combo = QComboBox()
        hnr_combo = QComboBox()

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
                'node': MeasureVoicePitch()
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
                'node': MeasureJitter() 
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
                'node': MeasureHNR()
            },
            'Measure Duration': {
                'type': 'Measure',
                'checked': False,
                'options': {},
                'node': MeasureVoiceDuration()
            },
            'Measure Intensity': {
                'type': 'Measure',
                'checked': False,
                'options': {},
                'node': MeasureIntensity()
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
                'node': MeasureShimmer()
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
                'node': MeasureVoiceFormant()
            },
            'Measure Vocal Tract': {
                'type': 'Measure',
                'checked': False,
                'options': {},
                'node': MeasureVocalTractEstimates()
            },
            'Measure Jitter PCA': {
                'type': 'Measure',
                'checked': False,
                'options': {},
                'node': MeasureJitterPCA()
            },
            'Measure Shimmer PCA': {
                'type': 'Measure',
                'checked': False,
                'options': {},
                'node': MeasureShimmerPCA()
            },
            'Measure Formant PCA': {
                'type': 'Measure',
                'checked': False,
                'options': {},
                'node': MeasureFormantPCA()
            },
            'Manipulate Pitch': {
                'type': 'Manipulate',
                'checked': False,
                'options': {},
                'node': ManipulatePitchNode()
            },
            'Manipulate Formant': {
                'type': 'Manipulate',
                'checked': False,
                'options': {},
                'node': ManipulateFormantsNode()
            },
            'Manipulate Pitch and Formant': {
                'type': 'Manipulate',
                'checked': False,
                'options': {},
                'node': ManipulatePitchAndFormants()
            },
            'Manipulate Gender and Age': {
                'type': 'Manipulate',
                'checked': False,
                'options': {},
                'node': ManipulateGenderAge()
            },
            'Visualize Spectrogram': {
                'type': 'Visualize',
                'checked': True,
                'options': {
                    'Band Width': {
                        'default_value': 0.05,
                        'widget': QLineEdit()
                    }
                },
                'node': PlotSpectrogram()
            },
            'Visualize Pitch': {
                'type': 'Visualize',
                'checked': True,
                'options': {
                    'Pitch Axis': {
                        'default_value': 500,
                        'widget': QLineEdit()
                    }
                },
                'node': PlotPitch()
            },
            'Visualize Intensity': {
                'type': 'Visualize',
                'checked': True,
                'options': {},
                'node': PlotIntensity()
            },
            'Visualize Formants': {
                'type': 'Visualize',
                'checked': True,
                'options': {},
                'node': PlotFormants()
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
        self.file_tab = FilesTab(self.feature_settings)
        self.settings_tab = SettingsTab(self.feature_settings)
        self.output_tab = OutputTab(self.feature_settings)

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

