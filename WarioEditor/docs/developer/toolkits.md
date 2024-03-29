# Building Toolkits

Multiple custom nodes can be combined into toolkits to allow for simplified repeat usage and sharing.

Toolkits are defined primarily by the ```config.json``` file stored in their root directory. This contains the toolkit parameters, list of global variables and list of nodes. The code for each node is stored in an individual file with the filename matching the classname of the node.

## Toolkit Parameters

The first component of the config file is the toolkit parameters. Currently, this is just the name of the toolkit and the location of the toolkits documentation relative to the root directory. 

```json
{
    "name" : "Example",
    "docs" : "./docs",
```

## Global Variables

Toolkits can be set to automatically include global variables that are required by their nodes. These globals have their name, attribute type and input method fixed but with the value being editable by the user.

Each global variable has 5 parameters:

| Parameter | Description | 
| :--- | :--- | 
| file | File containing global variable widget relative to the toolkit root folder | 
| class | Class of global variable widget | 
| toolkit | name of the toolkit holding the widget class |
| type | Attribute type of the global variable | 
| value | Default value | 
| properties | Properties of the widget (For custom widgets only) |
| const | Enables or disables constant value during pipeline runtime | 

To use the pre-made global variable widgets, set the file to ```extensions.globalWidgets```, the toolkit to ```wario```, and the class to one of the below:

| Widget Name | Description | 
| :--- | :--- | 
| GlobalTextbox | Single line text input box | 
| GlobalSpinbox | Int spinbox | 
| GlobalDoubleSpinbox | Double spinbox | 
| GlobalCheckbox | Checkbox | 
| GlobalFileSelect | Input textbox with button that opens file dialog | 
| GlobalFolderSelect | Input textbox with button that opens directory dialog | 
| GlobalListInput | Table that allows for a list of data to be input | 

NOTE: Custom global widgets are currently incompatable with toolkits due to how the current globals system loads the widgets. This will be fixed in a later update.

An example global variable is shown below:

```json
{
    "global_variables": {
        "Output Folder" : {
            "file" : "extensions.globalWidgets",
            "class" : "GlobalFolderSelect",
            "toolkit" : "wario",
            "type"  : "String",
            "value" : "./",
            "properties" : {},
            "const" : false
        }
    }
```

## Nodes

The final component of the toolkit is the list of nodes it contains. This is the most complex part of the config file, with each node containing 3 components, the core parameters, the attributes and the settings

### Node Parameters

These parameters tell WARIO how to render the node and give details on the location of the node's code

| Parameter | Description | 
| :--- | :--- | 
| file | The location of the file containing the node's code, relative to the toolkit root directory | 
| category | The category that the node will be listed under in the right-click new node menu |  

### Node Attributes

Attributes allow for connections to be made between nodes, so long as the attribute types match.

| Parameter | Description | 
| :--- | :--- | 
| connection | Sets the connection type of the attribute. Valid options are "input" or "output |
| type | The attribute type. Only attributes with matching types can be connected | 
| preset | OPTIONAL - Sets the attribute's visual style. Options are given in ./nodz/config.json |


### Node Settings

The settings parameter contains the file and class of the settings window that is used by the node. This allows for multiple nodes to share settings windows code

| Parameter | Description | 
| :--- | :--- | 
| settingsFile | Path to the settings file relative to the toolkit's root directory | 
| settingsClass | Name of the class in the settings file that contains the settings window | 

### Example Node

```json
{
    "node_types": {
        "Example Node" : {
            "file" : "exampleNode.py",
            "category" : "Examples",
            "attributes" : {
                "Input Attribute" : {
                    "connection" : "input",
                    "type" : "string"
                },
                "Output Attribute" : {
                    "connection" : "output",
                    "type" : "string"
                }
            },
            "settings" : {
                "settingsFile" : "exampleNode",
                "settingsClass" : "ExampleNodeSettings"
            }  
        }
    }
```

## Example Config File

Combining these parameters gives us the combined config.json file shown here:

```json
{
    "name" : "Example",
    "docs" : "./docs",
    "global_variables": {
        "Output Folder" : {
            "file" : "extensions.globalWidgets",
            "class" : "GlobalFolderSelect",
            "toolkit" : "wario",
            "type"  : "String",
            "value" : "./",
            "properties" : {},
            "const" : false
        }
    },
    "node_types": {
        "Example Node" : {
            "file" : "exampleNode.py",
            "category" : "Examples",
            "attributes" : {
                "Input Attribute" : {
                    "connection" : "input",
                    "type" : "string"
                },
                "Output Attribute" : {
                    "connection" : "output",
                    "type" : "string"
                }
            },
            "settings" : {
                "settingsFile" : "exampleNode",
                "settingsClass" : "ExampleNodeSettings"
            }  
        }
    }
}
```

## Documenting Toolkits

Toolkits should come with documentation in HTML format, stored within the toolkit's directory. This documentation is accessable as a tab in the WARIO editor's help window when the toolkit is activated.

It is recommended to use tools such as [Read The Docs](https://readthedocs.org/) that can host documentation created with libraries like [sphinx](https://www.sphinx-doc.org/en/master/index.html) or [mkdocs](https://www.mkdocs.org/) stored within a github repository. This allows for the creation of synchronized online and offline documentation, as seen with the WARIO editor.