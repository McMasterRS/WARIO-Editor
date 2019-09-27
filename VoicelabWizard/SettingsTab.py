from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class SettingsTab(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # all tabs have access to the parents data model
        # this contains the current state of data within the system including:
        # loaded file locations, results, and settings

        self.model = self.parent().model
