from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class ResultsModel(QAbstractListModel)
    def __init__(self, *args, results=None, **kwargs):
        super(ResultsModel, self).__init__(*args, **kwargs)
        self.results = results or []
