# Custom Nodes

Custom nodes require two core components to function, the Node class and the Settings class.

--------------------------------------

## The Node Class

All custom nodes must inheret from the Node class stored in the Pipeline folder. The name of the node class must match the name of the file it is contained within.

```python3
from pipeline.Node import Node
```

Each node contains the following functions

| Function | Description | 
| :---: | :--- | 
| init | Initializes the node. Must have a call to the parent node class. Any global class variables <br>that are needed for the node's execution can be placed here. <br><br> This is also a good place to perform input validation on any parameters such as inputted <br>file strings.| 
| start | Runs at beginning of pipeline after all nodes have been initialized | 
| process | This is the primary function of the node and takes the inputs from connected nodes and <br>performs necessary operations on them before outputting the results. | 
| end | This function runs on pipeline completion. It's particularly well suited to performing batch <br>processing where data is collected into a class variable during the "process" function. | 
| reset | Reserved for later use | 

### Node I/O

Data passed from child nodes can be accessed in the ```self.args``` class variable in each node but is only accessible during the "process" function call. This data is stored in a dict where the keys match the name of the relevant attribute of the node. 

``` python3
    data = self.args["Input Data"]
```

As there is no verification on the existance of attribute dat (nodes are ran once all *connected* child nodes are complete), you can make certain attributs optional by checking their existance in the list returned from ```self.args.keys()```, as seen in Example 1.

The "process" function must return a dict of outputs, who's keys match the names of the output attributes. While the attributes are given fixed types for ease of use while building the flowchart, any type of data can be passed using them.

```python3
    return {"Output Data" : outputData}
```

### Settings parameters

Parameters calculated by the settings window are stored as a dict in the ```self.parameters``` variable. This is accessabile from initialization of the node onwards. 

```python3 
    if self.parameters["showGraph"] == True:
        fig.show()
```

### Using Global Variables

Global variables are assigned to the node before the "process" function call and then any changes are extracted once the function is complete. these variables are stored as a dict in the ```self.global_vars``` class variable. The name if the global variable matches that shown in the global variables window in WARIO. While global variables used in toolkits are automatically inserted upon toolkit activation, any required for custom nodes must be added manually.

```python3
    globalFile = self.global_vars["Global File"]
```

Global variables can be modified as a part of any node's "process" function, but attempting to modify a global variable marked as constant will cause an error, resulting in the pipeline execution aborting.

--------------------------------------

## The Settings Class

The settings class works in much the same way as described in the [Custom Settings]() page with one small addition. As the node's attributes arent being pulled from a config file, a dict describing them must be included in the settings class inside the "getAttribs" function. Attributes are defined in the same format as described in [Building Toolkits](). An example of the getAttribs function is shown below

```python3

    def getAttribs(self):
        
        attribs = {
                    "Data": {
                        "index": -1,
                        "preset": "attr_preset_1",
                        "plug": True,
                        "socket": False,
                        "type": "csv"
                    }
                }
                
        return attribs
```
--------------------------------------

## Example Nodes:

### Example 1: List merger with settings

```python3
from pipeline.Node import Node
from extensions.customSettings import CustomSettings

from PyQt5 import QtWidgets
from PyQt5 import QtCore

class MergeListsSettings(CustomSettings):
    def __init__(self, parent, settings):
        super(MergeListsSettings, self).__init__(parent, settings)
        
    def buildUI(self, settings):
        self.layout = QtWidgets.QHBoxLayout()
        
        self.delDuplicates = QtWidgets.QCheckBox("Delete Duplicates")
        self.layout.addWidget(self.delDuplicates)
        if "deleteDuplicates" in settings.keys():
            self.delDuplicates.setChecked(settings["deleteDuplicates"])
        
        self.setLayout(self.layout)
        
    def genSettings(self):
        settings = {}
        vars = {}
        
        settings["settingsFile"] = self.settings["settingsFile"]
        settings["settingsClass"] = self.settings["settingsClass"]
        
        settings["deleteDuplicates"] = self.delDuplicates.isChecked()
        vars["deleteDuplicates"] = self.delDuplicates.isChecked()
        
        self.parent.settings = settings
        self.parent.variables = vars
        
    def getAttribs(self):
        attribs = {
                    "List 1": {
                        "index": -1,
                        "preset": "attr_preset_1",
                        "plug": False,
                        "socket": True,
                        "type": "list"
                    },
                    "List2": {
                        "index": -1,
                        "preset": "attr_preset_1",
                        "plug": False,
                        "socket": True,
                        "type": "list"
                    },
                    "List 3": {
                        "index": -1,
                        "preset": "attr_preset_1",
                        "plug": False,
                        "socket": True,
                        "type": "list"
                    },
                    "List 4": {
                        "index": -1,
                        "preset": "attr_preset_1",
                        "plug": False,
                        "socket": True,
                        "type": "list"
                    },
                    "Merged List": {
                        "index": -1,
                        "preset": "attr_preset_1",
                        "plug": True,
                        "socket": False,
                        "type": "list"
                    }
                }
                
        return attribs

class mergeLists(Node):
    
    def __init__(self, name, params):
        super(mergeLists, self).__init__(name, params)
    
    def process(self):
        
        list = []
        
        # Check each input attribute for a list
        # Allows for any number of the 4 nodes to be used
        for i in range(4):
            if "List {0}".format(i+1) in self.args.keys():
                list.append(self.args["List {0}".format(i+1)])
                
        # Delete duplicates if the setting is checked
        if self.parameters["deleteDuplicates"] == True:
            list = list(dict.fromkeys(list))
                
        return {"Merged List" : list}
````

### Example 2: Batch processing node class

```python3
from pipeline.Node import Node

class batchAvSignal(Node):
    def __init__(self, name, params):
        super(batchAvSignal, self).__init__(name, params)
        self.evokedArrays = []
        
    def process(self):
        
        evoked = self.args["Evoked Data"]
        self.evokedArrays.append(evoked)
   
        return
        
    def end(self):
        
        # Get array sizes that I need
        numArrays = len(self.evokedArrays)
        numEvents = len(self.evokedArrays[0])
        numChannels = len(self.evokedArrays[0][0].data)
        numTimes = len(self.evokedArrays[0][0].data[0])
        
        # Important information for later
        times = self.evokedArrays[0][0].times
        chNames = self.evokedArrays[0][0].info["ch_names"]
        eventNames = [e.comment for e in self.evokedArrays[0]]
        
        # Setup 4D numpy array to hold data
        data = np.zeros((numEvents, numChannels, numTimes, numArrays))

        # Transform data into required format
        # All subjects for all times for all channels for all events
        for i, evokedArray in enumerate(self.evokedArrays):
            for j, evoked in enumerate(evokedArray):
                for k, channel in enumerate(evoked.data):
                    for l, value in enumerate(channel):
                        data[j, k, l, i] = value
                    
        # data transformation makes getting statistics trivial
        means = np.mean(data, axis = 3)
        stdevs = np.std(data, axis = 3)
        
        # Save data as numpy data structure
        if self.parameters["toggleSaveData"]:
            f = self.parameters["saveGraphData"]
            np.savez(f, chNames = chNames,
                        eventNames = eventNames,
                        times = times,
                        mean = means,
                        std = stdevs)
```