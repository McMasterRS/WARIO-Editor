from pipeline.TaskFactory import NodeFactory
import importlib
import json

## Toolkits are mapped id's and class modules
## these in combination with a task factory allow you to flexibly create arbitrary nodes
class Toolkit():
    nodes = {}

    def __init__(self, toolkit_id):
        file_location = './toolkits/' + toolkit_id + '/config.json'
        self.toolkit_id = toolkit_id

        with open(file_location, 'r') as f:
            toolkit_definition = json.load(f)
            for node_id in toolkit_definition['node_types']:
                print(node_id)
                self.nodes[node_id] = toolkit_definition['node_types'][node_id]["file"].split('.')[0]

    def import_node(self, node_id):
        module_name = "toolkits." + self.toolkit_id + '.' + self.nodes[node_id]
        module = importlib.import_module(module_name)
        self.nodes[node_id] = getattr(module, self.nodes[node_id])
        return self.nodes[node_id]
    
    def add_node(self, node_id, type_id):
        pass
    
    def create_node(self, node_id):
        pass