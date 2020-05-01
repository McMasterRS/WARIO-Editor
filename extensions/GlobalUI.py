from PyQt5 import QtWidgets
from PyQt5 import QtCore
from wario.CustomWidgets import *
from wario.GlobalWidgets import *
import importlib
import os

# Global variable UI
class GlobalUI(QtWidgets.QWidget):
    def __init__(self, parent):
        super(GlobalUI, self).__init__()        
        
        self.vars = []
        self.parent = parent
        
        self.buildUI()
        
        self.resize(700, 300)
        self.setWindowIcon(self.style().standardIcon(getattr(QtWidgets.QStyle,"SP_TitleBarMenuButton")))
        self.setWindowTitle("Global Variables")
        
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.installEventFilter(self)
        
    def buildUI(self):
        self.layout = QtWidgets.QVBoxLayout()
        
        # Creates a QtTableView that requires unique keys in first column
        self.table = UniqueNameTable("Global variables must have unique names")
        self.table.setColumnCount(5)
        
        # Setup the header
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        self.table.setHorizontalHeaderLabels(['Variable Name', 'Type', 'Input Method', 'Value', 'Constant'])
        self.table.verticalHeader().setVisible(False)
        
        self.layout.addWidget(self.table)
        
        # Add/remove buttons
        buttonLayout = QtWidgets.QHBoxLayout()
        self.btAdd = QtWidgets.QPushButton(text = "Add")
        self.btAdd.clicked.connect(self.addRow)
        buttonLayout.addWidget(self.btAdd)
        
        self.btRemove = QtWidgets.QPushButton(text = "Remove")
        self.btRemove.clicked.connect(self.removeRow)
        buttonLayout.addWidget(self.btRemove)
        
        # Spacer to stop buttons from taking up entire row
        spacer = QtWidgets.QSpacerItem(100, 10, QtWidgets.QSizePolicy.Expanding)
        buttonLayout.addItem(spacer)
        
        self.layout.addLayout(buttonLayout)
        self.setLayout(self.layout)
        
    # Custom event filter to catch loss of focus/closing
    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.Close:
            
            self.genGlobals()
            event.accept()
        elif event.type() == QtCore.QEvent.WindowDeactivate:
            self.genGlobals()
            event.accept()
 
        return False
        
    # Updates all the global variables for all relevant parts of the code
    def genGlobals(self):
        globals = {}
        self.vars = {}
        
        # Loop through the rows and gather relevant data
        for row in range(0, self.table.rowCount()):
            gb = {}
            
            
            name = self.table.item(row, 0).text()                       
            attrType = self.table.item(row, 1).text().lower()
            type = self.table.cellWidget(row, 2).currentText()
            widget = self.table.cellWidget(row, 3)                      
            value = widget.getData()
            const = True if self.table.item(row, 4).checkState() == QtCore.Qt.Checked else False 
            properties = widget.getProperties()
            
            gb["file"] = widget.file            # File containing widget
            gb["class"] = widget.cls            # Class defining widget
            gb["toolkit"] = widget.toolkit      # Toolkit containing widget
            gb["attrType"] = attrType           # Data type
            gb["type"] = type                   # Input type
            gb["value"] = value                 # Value of global var
            gb["const"] = const                 # If global is constant
            gb["properties"] = properties       # Custom widget properties
            globals[name] = gb
            
            self.vars[name] = type
            
        # Send global variables to nodz_main to update nodes
        # TODO: Change this into a signal call
        self.parent.updateGlobals(globals)
            
        return globals
        
    # Load global variables a dict created by loading a JSON file
    def loadGlobals(self, globals):
    
        # If there are no globals, returnS
        if self.table.rowCount() == 0:
            return
            
        # Remove all non toolkit-essential rows
        for i in range(0, self.table.rowCount()):
            if self.table.cellWidget(i,2).isEnabled():
                self.table.removeRow(i)             
        
        # Add and fill all global variables
        for gb in globals:
            exists = False
            
            # Loop through the rows and see if the item already exists (toolkit-essential rows)
            for i in range(0, self.table.rowCount()):
                if self.table.item(i,0).text() == gb:
                
                    # Update toolkit-essential row
                    exists = True
                    row = i
                    value = self.genNewRowWidget(globals[gb])
                    self.table.setCellWidget(row, 3, value)
                    break
                
            # if its not a toolkit-essential row
            if exists == False:
                # Add the row
                self.addRow(globals[gb])
                row = self.table.rowCount() - 1

                # Create cell widgets
                self.table.item(row, 0).setText(gb)
                self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(globals[gb]["type"]))
                combo = self.table.cellWidget(row, 2)
                
                # Block signals so as not to trigger the combobox change function call until needed
                combo.blockSignals(True)
                
                # Use the data type of the global to work out which index to load 
                id = combo.findText(globals[gb]["type"])
                # Custom type
                if id == -1:
                    combo.setCurrentIndex(len(combo.items) - 1)
                else:
                    combo.setCurrentIndex(id)
                    
                combo.blockSignals(False)
                                
                # Check the constant checkbox if set to true
                if globals[gb]["const"]:
                    self.table.item(row, 4).setCheckState(QtCore.Qt.Checked)
                else:
                    self.table.item(row, 4).setCheckState(QtCore.Qt.Unchecked)      
                
                self.table.updateNames()
                
    # Generate input widget for new global row
    # This loads a custom widget from either the GlobalWidgets.py file in
    # the WARIO backend library or from a custom file stored with a toolkit
    # gb is a dict that contains all data for that particular global variable
    def genNewRowWidget(self, gb):
        # If the global dict is empty, assume its a text box
        if gb is None:
            return GlobalTextbox()
        
        # If dict exists but no input type file is specified, default to text box
        if "file" not in gb.keys():
            return GlobalTextbox()

        # See where the class is stored. Defaults to the WARIO directory
        if "toolkit" not in gb.keys():
            file = gb["file"]
            module = importlib.import_module(file)
        else:
            # Default location (WARIO backend library GlobalWidgets.py file)
            if gb["toolkit"] == "wario":
                file = gb["file"]
                module = importlib.import_module(file)
            else:
                # Custom toolkit UI location
                toolkit = self.parent.toolkitUI.toolkitPaths[gb["toolkit"]]
                file = os.path.join(toolkit, gb["file"])
                spec = importlib.util.spec_from_file_location(name = "Custom", location = file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

        # Generate instance of widget class
        cls = getattr(module, gb["class"])
        
        # Initialize widget
        widget = cls()
        widget.setData(gb)
        
        return widget
        
    # Generates function that swaps a row's input widget
    def changeWidgetGenerator(self, row):
        table = self.table
        def changeWidget(text):
            widget = None
            # Search for the widget based on the selected combobox text
            if text == "String":
                widget = GlobalTextbox()
            elif text == "Int":
                widget = GlobalSpinbox()
            elif text == "Float":
                widget = GlobalDoubleSpinbox()
            elif text == "Bool":
                widget = GlobalCheckbox()
            elif text == "File":
                widget = GlobalFileSelect()
            elif text == "Folder":
                widget = GlobalFolderSelect()
            elif text == "List":
                widget = GlobalListInput()
            elif text == "Custom":
                widget = GlobalCustomWidget()
                
            # Set as widget for the appropriate row
            table.setItem(row, 1, QtWidgets.QTableWidgetItem(text.lower()))
            table.setCellWidget(row, 3, widget)
                
        return changeWidget


    # Add a new row to the global variables table.
    # gb is the global variable (used when creating a row from a file)
    # name is the value in the name column. If none is give, it defaults to "Var<x>"
    # where <x> is a number starting at 0 and increasing each time a row is created
    def addRow(self, gb = None, name = None):
    
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        if name is None:
            name = "Var{0}".format(self.table.varNameCounter)
            self.table.varNameCounter += 1
        
        # Fixes an error when addRow is called by the button
        # The "clicked" call automatically assumes that the target function
        # takes "self" and a bool as its input parameters
        if isinstance(gb, bool):
            gb = None
        
        # Create the name and value widgets
        text = QtWidgets.QTableWidgetItem(name)
        value = self.genNewRowWidget(gb)
        
        # TypeComboBox defined in the GlobalWidgets file in the WARIO backend library
        combobox = TypeComboBox()
        # Connect change in text to unique function for each row. This allows the rows
        # to update their value widget independantly.
        combobox.currentTextChanged.connect(self.changeWidgetGenerator(self.table.rowCount() - 1))
        
        type = QtWidgets.QTableWidgetItem(combobox.currentText())
        
        # Checkbox that sets if the variable is constant or not
        checkbox = QtWidgets.QTableWidgetItem()
        checkbox.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        checkbox.setCheckState(QtCore.Qt.Unchecked)
        
        self.table.setItem(row, 0, text) 
        self.table.setItem(row, 1, type)        
        self.table.setCellWidget(row, 2, combobox)
        self.table.setCellWidget(row, 3, value)
        self.table.setItem(row, 4, checkbox)
        
    
    # Adds a toolkit-essential global variable and sets the flags to make only the value editable
    def addAutoRow(self, name, gb):

        # If the variable already exists then make it unremoveable
        if name in self.table.prevNames.values():
            for i in range(0, self.table.rowCount()):
                if self.table.item(i,0).text() == name:
                    self.table.item(i,0).setFlags(QtCore.Qt.NoItemFlags)
                    self.table.cellWidget(i,2).setCurrentText(gb["type"])
                    self.table.cellWidget(i,2).setEnabled(False)
                    self.table.item(i,4).setFlags(QtCore.Qt.NoItemFlags)
            return
        
        self.addRow(gb, name)
        row = self.table.rowCount() - 1
        
        # Set the flags so that only the value can be edited
        self.table.item(row,0).setFlags(QtCore.Qt.NoItemFlags)
        self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(gb["type"]))
        self.table.cellWidget(row,2).blockSignals(True)
        self.table.cellWidget(row,2).setCurrentText(gb["type"])
        self.table.cellWidget(row,2).setEnabled(False)
        self.table.cellWidget(row,2).blockSignals(False)
        self.table.item(row,4).setFlags(QtCore.Qt.NoItemFlags)
        
        if gb["const"]:
            self.table.item(row,4).setCheckState(QtCore.Qt.Checked)
        else:
            self.table.item(row,4).setCheckState(QtCore.Qt.Unchecked)
        
        
        self.genGlobals()

    def removeRow(self):
        if self.table.currentRow() != -1:
            # Verify that the row isnt toolbox-essential
            if self.table.item(self.table.currentRow(), 0).flags() & ~QtCore.Qt.ItemIsEnabled:
                self.table.removeRow(self.table.currentRow())
                self.table.updateNames()
                
    # Resets the flags for a row so that all cells can be edited
    def setRowsEditable(self):
        for row in range(0, self.table.rowCount()):
            self.table.item(row,0).setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)
            self.table.cellWidget(row,2).setEnabled(True)
            self.table.item(row,4).setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            
    def clearTable(self):
        while self.table.rowCount() > 0:
            self.table.removeRow(0)
            
        self.table.prevNames = {}
            