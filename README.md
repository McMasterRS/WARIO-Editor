# WARIO - Workplace Automation for Research I/O

A flowchart based data pipeline development suit with an interface extended from the [Nodz](https://github.com/LeGoffLoic/Nodz) library.

![Wario Example](https://github.com/McMasterRS/WARIO-Editor/blob/master/WarioEditor/docs/Images/WARIO_example.png)

## Features
* Easy to use flowchart system to create and connect nodes
* Allows for the development of fully working python pipelines 
* Supports batch processing and bulk data analysis
* Supports the creation of custom node sets with the built in toolkit system
* Fully customizable settings UI for all nodes
* Global variable system that can be accessed by all nodes during runtime
* Signal passing using the [Blinker](https://pythonhosted.org/blinker/) library

## Documentation

Documentation is hosted on [readthedocs](https://wario.readthedocs.io/en/latest/) and a local version is accessible from the help menu within the editor

## Installation

1. download and unzip the WARIO Editor
2. Install the editor and its requirements as a module by navigating to the WARIO Editor folder and running `pip install .`
3. Run pip -m WarioEditor

## Requirements
```
- Python 3
- PyQt5
- PyQtWebEngine
- Blinker
- Graphviz
- Wario
```
