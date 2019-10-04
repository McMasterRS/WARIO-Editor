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
        self.existing_stack = None

        self.measure_layout = QVBoxLayout()
        self.measure_list = QListWidget()
        self.measure_stack = QStackedWidget()

        self.list_stacks = {}
        self.stack_layouts = {}
        self.stack = QStackedWidget(self)

        self.default_params_toggle = QCheckBox("Use Custom Parameters")
        self.default_params_toggle.stateChanged.connect(self.toggle_defaults)

        self.reset_defaults = QPushButton()
        self.reset_defaults.setText('Reset all to defaults')
        self.reset_defaults.clicked.connect(self.on_reset)

        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)

        self.list_items = {}
        self.leftlist = QListWidget()

        left_layout.addWidget(self.leftlist)
        left_layout.addWidget(self.reset_defaults)

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(left_widget)
        self.layout.addWidget(self.stack)

        self.setLayout(self.layout)
        self.leftlist.currentRowChanged.connect(self.display)
        self.leftlist.itemChanged.connect(self.onchange_check)
        self.display_options()

    ###############################################################################################

    def display_options(self):

        # If there are already pages in the stack, delete them and recreate them
        self.leftlist.itemChanged.disconnect()

        for feature in self.model['functions']:

            checked = self.model['functions']['Measure Pitch']['checked']

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

        self.leftlist.itemChanged.connect(self.onchange_check)

    def toggle_defaults(self):
        print('toggle')

    def onchange_check(self, e):
        self.model['functions'][e.text()]['checked'] = e.checkState()
        print(self.model['functions'][e.text()]['checked'])
        # if e.checkState() == Qt.Unchecked:
        #     self.model['functions'][e.text()]['checked'] = Qt.Checked
        # elif e.checkState() == Qt.Checked or e.checkState() == Qt.PartiallyChecked:
        #     self.model['functions'][e.text()]['checked'] = Qt.Unchecked

    def display(self,i):
        self.stack.setCurrentIndex(i)

    def on_reset(self):
        self.leftlist.clear()
        self.stack_layouts = {}
        self.list_stacks = {}
        n_stacks = self.stack.count()
        for i in range(n_stacks):
            self.stack.widget((n_stacks-1)-i).setParent(None)

        for fn in self.model['functions']:
            fn_node = self.model['functions'][fn]['node']
            fn_node.args = self.model['defaults'][fn]['value']

            self.model['functions'][fn]['checked'] = self.model['defaults'][fn]['checked']

            
        self.display_options()