# Custom Global Inputs

Global variables are able to be input into WARIO in multiple ways but on occasion it is necessary for a more complex input interface to be used. In these cases, custom interfaces based on the ```GlobalWindowWidget``` class in ```extensions.globalWidgets``` can be used.

## Building A Custom Interface

All classes that are to be used as global variable interfaces must inheret the ```GlobalWindowWidget``` class. The following is a guide on how to correctly set up a custom interface

### 1 - Initialization

As with the settings window, the class must be initialized. The ```GlobalWindowWidget``` class has no initialization parameters so this is a simple process.

```python3
from extensions.globalWidgets import GlobalWindowWidget

class ExampleGlobalWidget(GlobalWidgetWindow):
    def __init__(self):
        super(ExampleGlobalWidget, self).__init__()
```

### 2 - Building your interface

The interface for the widget can be built in the same way as described in step 2 of the [Custom Settings Guide](settings). The key difference is that in this case, the interface must be built in the ```__init__``` function. 

The parent class contains a pre-made ```QHBoxLayout``` layout assigned to the ```self.layout``` variable. This has a reduced margin that makes sure that the interface is not placed too close to the window margins. This can be overloaded if necessary.

```python3
    self.textbox = QtWidgets.QLineEdit()
    self.layout.addWidget(self.textbox)
```

This gives a final initialization function of

```python3
from extensions.globalWidgets import GlobalWindowWidget
from PyQt5 import QtWidgets

class ExampleGlobalWidget(GlobalWidgetWindow):
    def __init__(self):
        super(ExampleGlobalWidget, self).__init__()
        self.textbox = QtWidgets.QLineEdit()
        self.layout.addWidget(self.textbox)
```

### 3 - Setting up the data collection function

The values of the global variables is gathered by looping over each row in the table and calling the ```getData``` function. This returns an object or variable that contains all the data required by the code to use that global variable

```python3
def getData(self):
    return self.texbox.text()
```

### 4 - Setting up the interface loading function

When a file is loaded, the global variable interface loops through each row and calls the ```setData``` function, passing the dict containing all the information on that row's global variable. This is used to initialize the data within that interface. The data given by the ```getData``` function is stored under the key "value".

```python3
def setData(self, gb):
    self.textbox.setText(gb["value"])
```

### Finished Custom Global Widget

```python3
from extensions.globalWidgets import GlobalWindowWidget
from PyQt5 import QtWidgets

class ExampleGlobalWidget(GlobalWidgetWindow):
    def __init__(self):
        super(ExampleGlobalWidget, self).__init__()
        self.textbox = QtWidgets.QLineEdit()
        self.layout.addWidget(self.textbox)
        
    def getData(self):
        return self.texbox.text()
        
    def setData(self, gb):
        self.textbox.setText(gb["value"])
```

## Complex interfaces

More complex interfaces  may require more data to initialize than is used by the code to operate on the global variables. When this is the case, we can define additional properties through the ```getProperties``` function. These properties are stored in the "properties" key in the global variable's dict and can be access in the ```setData``` function.

To use this function, return a dict containing any relevant data. Be aware that this function is called when a new instance of the interface is created and therefore the list of properties must be checked to make sure they contain the relevant keys.

```python3
    def getProperties(self):
        tabID = self.tabs.currentIndex()
        mode = self.modeCombo.currentIndex()
        
        return {"tabID" : tabID, "mode" : mode}
        
    def setData(self, gb):
        if "tabID" in gb["properties"].keys():
            self.tabs.setCurrentIndex(gb["properties"]["tabID"])
        if "mode" in gb["properties"].keys():
            self.modeCombo.setCurrentIndex(gb["properties"]["mode"])
```