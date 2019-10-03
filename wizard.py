import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from VoicelabWizard.InputTab import InputTab
from VoicelabWizard.OutputTab import OutputTab
from VoicelabWizard.SettingsTab import SettingsTab

from VoicelabWizard.DefaultSettings import default_settings, avialable_functions, default_functions

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

        # Persistant data throughout the system
        self.model = {
            'files': [],        # Collection of currently loaded voice files
            'functions': {},    # Collection of available functions
            'results': {
                'functions': {},
                'files': {}
            }
        }

        # Set up the internal state for whether a function is checked
        for fn in avialable_functions:
            self.model['functions'][fn] = {
                'checked': True if fn in default_functions else False,
                'node': avialable_functions[fn]
            }

        tabs.addTab(InputTab(parent=self), "Input")
        tabs.addTab(OutputTab(parent=self), "Output")
        tabs.addTab(SettingsTab(parent=self), "Settings")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = VoicelabWizard()
    w.show()
    sys.exit(app.exec_())
