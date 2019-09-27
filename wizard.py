import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from VoicelabWizard.InputTab import InputTab
from VoicelabWizard.OutputTab import OutputTab
from VoicelabWizard.SettingsTab import SettingsTab

from VoicelabWizard.DefaultSettings import feature_defaults

class VoicelabWizard(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setMinimumSize(QSize(640, 480))    
        self.setWindowTitle("Voicelab")

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        central_layout = QGridLayout(self)
        central_widget.setLayout(central_layout)

        tabs = QTabWidget()
        central_layout.addWidget(tabs)

        self.model = {
            'files': [],    # loaded voice files
            'results': [],  # ordered list of results corresponding with each loaded file
            'features': {}, # settings for each feature, keyed by feature name
        }

        for feature in feature_defaults:
            self.model['features'][feature] = {
                'checked': False,
                'parameters': feature_defaults[feature]
            }

        tabs.addTab(InputTab(parent=self), "Input")
        tabs.addTab(OutputTab(parent=self), "Output")
        tabs.addTab(SettingsTab(parent=self), "Settings")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = VoicelabWizard()
    w.show()
    sys.exit(app.exec_())
