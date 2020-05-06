# Custom Settings

Custom settings are built off of the ```CustomSettings``` class in ```extensions.customSettings```. They create an interface between the user and the code while avoiding the need for direct coding experience.

## Building A Basic Custom Settings Window
Below is a step by step guide on how to create a new custom node.

### 1 - Initialization

The node must be created and the parent class initialized to make sure that the rest of the class has access to the parent and settings variables. Unlike with the custom nodes, the settings class can be named anything the user wishes, although the format of "NodeClassNameSettings" is used by the WARIO development team for consistancy.

```python3
from extensions.customSettings import CustomSettings

class ExampleNodeSettings(CustomSettings):
    def __init__(self, parent, settings):
        super(ExampleNodeSettings, self).__init__(parent, settings)
```

### 2 - Constructing The Settings UI

The ```buildUI``` function is called as a part of the initialization of the ```CustomSettings``` class. As the  parent class itself inherets from the PyQt5 ```QWidget``` class, we can use widgets included in PyQt5 to build our interface.

The first required component is the layout object

```python3
    def buildUI(self, settings):
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
```

In this example we're using the ```QVBoxLayout``` object which creates a vertical arrangement of widgets but other layout types can be found at the [Qt documentation site](https://doc.qt.io/qt-5/qhboxlayout.html). While this documentation is given in C++, the function calls are effectively identical.

Widgets can be added to this layout to give the required settings interface. In this example we're adding a single checkbox that enables or disables a graphical output

```python3
        self.showGraph = QtWidgets.QCheckBox("Show Graph")
        self.layout.addWidget(self.showGraph)
```

Combined, this gives

```python3
    def buildUI(self, settings):
        self.layout = QtWidgets.QVBoxLayout()
        
        self.showGraph = QtWidgets.QCheckBox("Show Graph")
        self.layout.addWidget(self.showGraph)
        
        self.setLayout(self.layout)      
```

Alternatively, it is possible to import .ui files created in software like QT-Designer. To import a .ui file use the following code

```python3
	uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)),"uiFileRelativeToNodeFile.ui"), self)
```

The os.path commands generate a path to the ui file relative to the node's .py file, allowing you to create settings UIs for custom toolkits. This command assigns all widgets to be children of ```self``` and thus you can access them by referencing the names set in the designer, e.g.

```python3
self.labelWidget.setText("text to set")
```

### 3 - Generating The Settings Output

The final required function is ```genSettings```. This is called when the settings window is closed, loses focus, or the WARIO editor saves a file. This function generates two dicts, one for the properties of the settings widgets and the other for the values of the variables used by the code.

First, we need to store the "settingsFile" and "settingsClass" values. These are used to locate the file and class that defines the node's settings UI when loading a WARIO pipeline.

```python3
    def genSettings(self):
        settings = {}
        vars = {}
        
        settings["settingsFile"] = self.settings["settingsFile"]
        settings["settingsClass"] = self.settings["settingsClass"]
```

With those values saved, the current state of all the window's widgets must be gathered. These values can be given any key but it is recommended to use consistant, easy to understand names.

```python3
        settings["showGraphToggleState"] = self.showGraph.getChecked()
```

Likewise, the values given by relevant widgets must be stored. The keys of these values must match those used by the node's code.

```python3
        vars["showGraph"] = self.showGraph.getChecked()
```

Finally, the node that the settings window is attached to must be passed the settings and variable values

```python3
        self.parent.settings = settings
        self.parent.variables = vars
```

This gives the full ```genSettings``` function as shown below

```python3
    def genSettings(self):
        settings = {}
        vars = {}
        
        settings["settingsFile"] = self.settings["settingsFile"]
        settings["settingsClass"] = self.settings["settingsClass"]
        
        settings["showGraphToggleState"] = self.showGraph.getChecked()
        vars["showGraph"] = self.showGraph.getChecked()
        
        self.parent.settings = settings
        self.parent.variables = vars
```

### 4 - Handling Loading

Now that there is a system in place for saving the state of the settings window, code must be added to ```buildUI``` to make sure that the widgets are properly updated upon loading a pipeline. As the function must be able to handle both new and loaded settings windows, we must check if to see if each key exists before applying

```python3
    def buildUI(self, settings):
        self.layout = QtWidgets.QVBoxLayout()
        
        self.showGraph = QtWidgets.QCheckBox("Show Graph")
        if "showGraphToggleState" in settings.keys():
            self.showGraph.setChecked(settings["showGraphToggleState"])
        self.layout.addWidget(self.showGraph)
        
        self.setLayout(self.layout)              
```
### Finished Settings Window

The above tutorial gives the following settings window:

```python3
from extensions.customSettings import CustomSettings
from PyQt5 import QtWidgets

class ExampleNodeSettings(CustomSettings):
    def __init__(self, parent, settings):
        super(ExampleNodeSettings, self).__init__(parent, settings)
        
    def buildUI(self, settings):
        self.layout = QtWidgets.QVBoxLayout()
        
        self.showGraph = QtWidgets.QCheckBox("Show Graph")
        if "showGraphToggleState" in settings.keys():
            self.showGraph.setChecked(settings["showGraphToggleState"])
        self.layout.addWidget(self.showGraph)
        
        self.setLayout(self.layout) 

    def genSettings(self):
        settings = {}
        vars = {}
        
        settings["settingsFile"] = self.settings["settingsFile"]
        settings["settingsClass"] = self.settings["settingsClass"]
        
        settings["showGraphToggleState"] = self.showGraph.getChecked()
        vars["showGraph"] = self.showGraph.getChecked()
        
        self.parent.settings = settings
        self.parent.variables = vars
```

## Optional Functions

There are several additional functions included in the CustomSettings class that can be overloaded.

### updateGlobals

The ```updateGlobals``` function is used for widgets that require access to the global variable values. This could be used for such things as global file naming or changing widget properties. The base version of this function is defined as follows, with "globals" containing the dict of global variables in the same manner as used in the code (see [Custom Nodes](nodes))

```python3
    def updateGlobals(self, globals):
        return
```

### getAttribs

The ```getAttribs``` function is used exclusively when defining the attributes for nodes to be used by the "Custom Node" pipeline node. See [Custom Nodes](nodes) for more information.

### eventFilter

The ```eventFilter``` function is an overload of the built in PyQt5 version of the function that runs the ```genSettings``` function when the settings window is either closed or loses focus. This allows for the settings window to directly affect the node's properties such as its name or attributes.

The default version of this functionis as follows

```python3

    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.Close:
            self.genSettings()
            event.accept()
        elif event.type() == QtCore.QEvent.WindowDeactivate:
            self.genSettings()
            event.accept()
            
        return False     
```

## Custom Widgets

Sometimes, its easier to create an overloaded PyQt widget class that can be reused for multiple nodes. Several of these have been developed for WARIO and can be found in the ```extensions.customWidgets``` file in the WARIO directory. Below are some of the more widely useful ones.

### saveWidget/loadWidget

Shows a textbox with a button that opens a dialog allowing save/load locations to be set respectively. Can be passed a string that sets the dialog filter. 

Must be passed the parent widget.

```python3
    textSave = saveWidget(self, "Text files (*.txt)")
```

### UniqueNameTable

A QTableWidget that forces unique values in the first column. Any attempt to use a value that already exists causes the cell to revert to its previous value. It includes the ```changedTextHook``` function that can be overloaded to perform tasks when the user changes the text in any cell of the first column

```python3
    def changedTextHook(self, row):
        return
```

Must be initialized with string containing the error text for when the user attempts to enter an existing name

```python3
    uniqueTable = UniqueNameTable("Cannot have identical keys")
````

### LinkedCheckbox

A checkbox that can be linked to another widget to enable or disable it depending on the state of the checkbox. Includes the functions ```buildLinkedCheckbox``` and ```getSettings```. The former loads the state of the checkbox and the latter generates the settings and variables for the widget. If the linked widget is either a QComboBox or QSpinBox, they also handle setup and saving for the widget.

```python3
    # In self.buildUI
    self.enableWidget = LinkedCheckbox("Enable Widget", existingWidget)
    self.enableWidget.buildLinkedCheckbox("enableWidget", settings)
    
    # In self.genSettings
    self.enableWidget.getSettings("enableWidget", vars, settings)
```

If a spinbox or combobox, the variable name of the setting is given by the name passed to the getSettings function and its value is set to "None" if the checkbox is left unchecked.

### LinkedSpinbox/LinkedDoubleSpinbox

These widgets allow you two create 2 spinboxes of either int or double type that are linked together so as to limit the range of each. The ```linkWidgets``` function is used to set the linked widget and how they act relative to the widget calling the function

The LinkedSpinbox widget will force the spinbox values to be no closer than 1 from each other and the LinkedDoubleSpinbox no closer than 0.01

```python3
    self.maxValue = LinkedSpinbox()
    self.minValue = LinkedSpinbox()
    
    # We want the min value to always be lower than the max value
    self.maxValue.linkWidgets(self.minValue, "Lower")
    # And the max value to always be higher than the min value
    self.minValue.linkWidgets(self.maxValue, "Higher")
```

### ExpandingTable

This creates a 1 column table that automatically expands when a value is inserted into the final row. It also shrinks whenever the final row is emptied. As with the LinkedCheckbox widget, this widget has a ```getSettings``` function that allows for the values stored in the table to be extracted with a single line. The key for these variables is the name passed to the init and getSettings functions (which must be identical)

```python3
    # In self.buildUI
    self.table = ExpandingTable("data", settings)
    
    # in self.genSettings
    self.table.getSettings("data", vars, settings)
```
    
### CentredCellCheckbox

A widget that mimics a checkbox that can be used in QTableWidgets. This creates a centred checkbox that looks more tidy than the default left-aligned one when a cell is simply set as checkable. The functions ```setChecked``` and ```isChecked``` work in the same way as with a regular QCheckBox widget, and the ```connect``` function acts in the same way as the ```checkbox.toggled.connect``` call would.

```python3
    checkbox = CentredCellCheckbox()
    table.addWidget(0, 0, checkbox)
```
