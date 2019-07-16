import json

NODZ_SAVE = "./pipeline/saves/sample.json"

class ImportLayer():
    """  Consolidates external interfacing to a single place.  """

    tasks = {}
    connections = {}

    def __init__(self):
        pass

class NodzImporter():

    def __init__(self):
        raw = self.load(NODZ_SAVE)
        parsed = self.parse(raw)
        self.parsed = parsed

    def load(self, location):
        with open(location, 'r') as f:
            data = json.load(f)
        return data

    def parse(self, data):
        """ """
        nodz = NodzDefinition(data)

        tasks = {}
        task_types = {}
        connections = {}
        variables = {}

        # Populates the types of tasks, key = task type string, value = the file name
        for nod in data["NODES"]:

            task_name = nod
            task_signature = {
                "in": [],
                "out": [],
                "variables": None,
                "type": None
            }

            for attribute in data["NODES"][nod]["attributes"]:
                if attribute["plug"]:
                    task_signature["out"].append(attribute["name"])
                if attribute["socket"]:
                    task_signature["in"].append(attribute["name"])
            
            task_signature["variables"] = data["NODES"][nod]["variables"] # silly name mismatch here, should standardize the name of things
            task_signature["type"] = data['NODES'][nod]["type"]
            tasks[task_name] = task_signature

            task_type = data["NODES"][nod]["type"]
            file_location = data["NODES"][nod]["file"].split(".")[0] #TODO: The nodz saves are formated 'file'.py. we dont want the py
            task_types[task_type] = file_location

            connections[nod] = {}
            variables[nod] = task_signature["variables"]

        # Populates the connections
        for connection in data["CONNECTIONS"]:

            parent_name = connection[0].split(".")[0]
            parent_attribute = connection[0].split(".")[1]
            child_name = connection[1].split(".")[0]
            child_attribute = connection[1].split(".")[1]
            if parent_attribute not in connections[parent_name]:
                connections[parent_name][parent_attribute] = []
            connections[parent_name][parent_attribute].append([child_name, child_attribute])
            # connections[child_name][child_attribute] = [parent_name, parent_attribute]

        return [task_types, tasks, connections, variables]

from pipeline.NodeFactory import NodeFactory

class PipelineDefinition():
    nodes = {}
    node_types = []
    global_vars = [] 

    def __init__(self):
        pass
    def __str__(self):
        return "nope"

class NodzDefinition():
    def __init__(self, json, factory=None):
        self.nodes = {}
        self.configuration_parameters = []
        self.node_types = []
        self.globals = []
    def parse_json_definition(self, json_definition):
        
        for node_name in json["NODES"]:
            node = json["NODES"][node_name]
            self.nodes.append(node)
            self.node_types.append(node["type"])
            self.configuration_parameters.append()

            node_type = node["type"]
            params = node['params']

            self.node_types.append(node_type)
            self.node[node_name] =
            print("Node", node)

        for connection_name in json["CONNECTIONS"]:
            print("Connection", connection_name)


from pipeline.TaskFactory import TaskFactory as NodeFactory

LOADED_DEFINITIONS = {
    "nodz": NodzDefinition
}


### Creates a collection of nodes from a compatible pipeline definition
### also creates a factory definition for creating new nodes

class PipelineLoader():

    def __init__(self, factory=None):
        self.factory = NodeFactory() if factory is not None else factory

    def load_from_file(self, fs_location):
        pass

    def load_from_url(self, url):
        pass

class NodzDefinition():
    def __init__(self):
        pass