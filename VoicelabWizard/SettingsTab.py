from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

###################################################################################################
###################################################################################################

class SettingsTab(QWidget):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.model = self.parent().model
        self.feature_settings = {}
        self.initUI()

    def initUI(self):

        self.layout = QVBoxLayout()

        self.is_active = True
        self.advanced_toggle = QCheckBox("Use Advanced Settings")
        self.advanced_toggle.stateChanged.connect(self.toggle_settings)

        self.measure_settings = MeasureSettings(self.model)
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

    def __init__(self, model):

        super().__init__()
        self.model = model

        self.measure_layout = QVBoxLayout()
        self.measure_list = QListWidget()
        self.measure_stack = QStackedWidget()

        self.default_params_toggle = QCheckBox("Use Custom Parameters")
        self.default_params_toggle.stateChanged.connect(self.toggle_defaults)

        self.list_items = {}
        self.list_stacks = {}
        self.stack_layouts = {}
        self.leftlist = QListWidget()
        self.stack = QStackedWidget(self)
        
        for feature in self.model['functions']:

            # Add this option to the list with appropriate text and checkbox
            self.list_items[feature] = QListWidgetItem(parent=self.leftlist)
            self.list_items[feature].setText(feature)
            self.list_items[feature].setCheckState(self.model['functions'][feature]['checked'])

            # Add the appropriate configuration widgets
            self.list_stacks[feature] = QWidget()
            self.stack.addWidget(self.list_stacks[feature])
            self.stack_layouts[feature] = QFormLayout()

            for parameter in self.model['functions'][feature]['node'].args:
                
                param_value = self.model['functions'][feature]['node'].args[parameter]

                if isinstance(param_value, tuple):
                    widget = QComboBox()
                    widget.addItem(param_value[0])
                    for item in param_value[1]:
                        widget.addItem(item)
                else:
                    widget = QLineEdit()
                    widget.setText(str(param_value))

                self.stack_layouts[feature].addRow(parameter, widget)

            self.list_stacks[feature].setLayout(self.stack_layouts[feature])

        hbox = QHBoxLayout(self)
        hbox.addWidget(self.leftlist)
        hbox.addWidget(self.stack)

        self.setLayout(hbox)
        self.leftlist.currentRowChanged.connect(self.display)
        self.leftlist.itemChanged.connect(self.onchange_check)

    ###############################################################################################

    def toggle_defaults(self):
        print('toggle')

    def onchange_check(self, e):

        if e.checkState() == 2:
            self.model['functions'][e.text()]['checked'] = True
        else:
            self.model['functions'][e.text()]['checked'] = False

    def display(self,i):
        self.stack.setCurrentIndex(i)