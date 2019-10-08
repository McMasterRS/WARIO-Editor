from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import types
import copy 
###################################################################################################
###################################################################################################

class SettingsTab(QWidget):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.model = self.parent().model
        self.cached = None

        # The default settings are presumed to be the settings this initialized with
        self.default_settings = copy.deepcopy(self.model['settings'])

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
    
    def toggle_settings(self, checked):
        if checked: # If this is disabled
            self.cached = self.model['settings']
            self.model['settings'] = self.default_settings
            self.measure_settings.setDisabled(not bool(checked))
        else:
            self.model['settings'] = self.cached
            self.measure_settings.setDisabled(not bool(checked))

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


    ###############################################################################################

    def display_options(self):

        self.active_functions = {}
        self.current_settings = {}

        for fn_name in self.model['settings']:

            check_state = self.model['settings'][fn_name]['checked']
            self.current_settings[fn_name] = {}

            # Add this option to the list with appropriate text and checkbox
            self.list_items[fn_name] = QListWidgetItem(parent=self.leftlist)
            self.list_items[fn_name].setText(fn_name)
            self.list_items[fn_name].setCheckState(check_state)

            # Add the appropriate configuration widgets
            self.list_stacks[fn_name] = QWidget()
            self.stack.addWidget(self.list_stacks[fn_name])
            # self.stack_layouts[fn_name] = QFormLayout()
            self.stack_layouts[fn_name] = QVBoxLayout()
            self.stack_layouts[fn_name].setAlignment(Qt.AlignTop)

            if len(self.model['settings'][fn_name]['value']) == 0:
                label = QLabel()
                label.setText('No settings to  configure')
                self.stack_layouts[fn_name].addWidget(label)
            else:
                for parameter in self.model['settings'][fn_name]['value']:
                    param_value = self.model['settings'][fn_name]['value'][parameter]

                    # If there are options, display them as a combo box
                    if isinstance(param_value, tuple):
                        widget = ComboSetting(parameter, param_value, fn_name, model=self.model)

                    # If this is a function of some sort
                    elif callable(param_value):
                        widget = FunctionSetting(parameter, param_value, fn_name, model=self.model)

                    # Otherwise just assume some sort of text input
                    else:
                        widget = SettingWidget(parameter, param_value, fn_name, model=self.model)

                    self.stack_layouts[fn_name].addWidget(widget)

            self.list_stacks[fn_name].setLayout(self.stack_layouts[fn_name])

    def onchange_check(self, e):
        self.model['settings'][e.text()]['checked'] = e.checkState()

    def display(self, i):
        self.stack.setCurrentIndex(i)

    def on_reset(self):
        self.leftlist.clear()
        self.stack_layouts = {}
        self.list_stacks = {}
        n_stacks = self.stack.count()
        
        # Remove the current widgets on the stack
        for i in range(n_stacks):
            self.stack.widget((n_stacks-1)-i).setParent(None)

        # Reset the fn_arguments
        for fn in self.model['functions']:
            fn_node = self.model['functions'][fn]['node']
            fn_node.args = self.model['defaults'][fn]['value']

            self.model['functions'][fn]['checked'] = self.model['defaults'][fn]['checked']

        self.display_options()

class SettingWidget(QWidget):
    def __init__(self, name, default, fn_name, model=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.default = default
        self.inactive = True
        self.cached = default
        self.model = model
        self.name = name
        self.type = type(default)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel()
        self.label.setText(str(name))

        self.checkbox = QCheckBox()
        self.checkbox.stateChanged.connect(self.toggle)
        self.lineedit = QLineEdit()
        self.lineedit.setDisabled(self.inactive)
        self.lineedit.setText(str(self.default))
        self.lineedit.textChanged.connect(self.on_textchanged)

        self.layout.addWidget(self.checkbox)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.lineedit)
    
    # Toggle resets the control widget and it's bound value to the default settings
    def toggle (self, e):
        self.inactive = not self.inactive
        self.lineedit.setDisabled(self.inactive)
        if self.inactive:
            self.cached = self.lineedit.text()
            self.lineedit.setText(str(self.default))
            self.model['settings'][self.fn_name]['value'][self.name] = self.default
        else:
            self.lineedit.setText(str(self.cached))
            self.model['settings'][self.fn_name]['value'][self.name] = self.cached

    def reset(self):
        self.bound_variable = self.default
        self.cached = self.default
        self.inactive = True

    def on_textchanged(self, new_text):

        if isinstance(self.default, int):
            self.model['settings'][self.fn_name]['value'][self.name] = int(new_text)

        elif isinstance(self.default, float):
            self.model['settings'][self.fn_name]['value'][self.name] = float(new_text)

        elif isinstance(self.default, str):
            self.model['settings'][self.fn_name]['value'][self.name] = new_text

    @property
    def value (self):
        return self.lineedit.text()

class FunctionSetting(QWidget):
    def __init__(self, name, default, fn_name, model=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.name = name
        self.model = model
        self.fn_name = fn_name
        self.inactive = True
        self.cached = ''
        self.default = default
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel()
        self.label.setText(str(name))

        self.checkbox = QCheckBox()
        self.checkbox.stateChanged.connect(self.toggle)
        self.lineedit = QLineEdit()
        self.lineedit.setDisabled(self.inactive)
        self.lineedit.setText('Automatic')

        self.layout.addWidget(self.checkbox)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.lineedit)
    
    def toggle (self, e):
        self.inactive = not self.inactive
        self.lineedit.setDisabled(self.inactive)

        if self.inactive:
            self.cached = self.lineedit.text()
            self.lineedit.setText('Automatic')
            self.model['settings'][self.fn_name]['value'][self.name] = self.default

        else:
            self.lineedit.setText(self.cached)
            self.model['settings'][self.fn_name]['value'][self.name] = self.cached

    @property
    def value (self):
        if self.inactive:
            return self.default

        return lambda: self.lineedit.text()

class ComboSetting(QWidget):
    def __init__(self, name, default, fn_name, model=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.default = default[0]
        self.inactive = True
        self.cached = self.default
        self.model = model
        self.name = name
        self.fn_name = fn_name

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel()
        self.label.setText(str(name))
        self.label.setAlignment(Qt.AlignLeft)

        self.checkbox = QCheckBox()
        self.checkbox.stateChanged.connect(self.toggle)

        self.combobox = QComboBox()

        for item in default[1]:
            self.combobox.addItem(item)
        self.combobox.setCurrentText(self.default)

        self.combobox.setDisabled(self.inactive)
        self.combobox.currentIndexChanged.connect(self.on_statechanged)

        self.layout.addWidget(self.checkbox)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.combobox)
    
    def toggle (self, e):

        self.inactive = not self.inactive
        self.combobox.setDisabled(self.inactive)

        if self.inactive:
            self.cached = self.combobox.currentText()
            self.combobox.setCurrentText(str(self.default))
            self.model['settings'][self.fn_name]['value'][self.name] = self.default

        else:
            self.combobox.setCurrentText(str(self.cached))
            self.model['settings'][self.fn_name]['value'][self.name] = self.cached

    def on_statechanged(self, e):
        self.model['settings'][self.fn_name]['value'][self.name] = type(self.default)(self.combobox.currentText())
        print(e)

    @property
    def value (self):
        return self.combobox.currentText()