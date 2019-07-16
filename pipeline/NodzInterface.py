import json
from pipeline.TaskFactory import NodeFactory

NODZ_SAVE_LOCATION = "./pipeline/saves/sample.json"

class NodzInterface():

    @staticmethod
    def load(file_location):

        nodes_mapping = {}
        nodes = []
        connections = []
        global_vars = {}

        with open(file_location, 'r') as f:
            data = json.load(f)

            if "NODES" in data:
                for node_id in data["NODES"]:
                    node = data["NODES"][node_id]
                    print(node['variables'])
                    class_name = node["file"].split('.')[0]
                    NodeFactory.import_node(node["type"], node["toolkit"], class_name)
                    node_instance = NodeFactory.create_node(node_id, node["type"])
                    node_instance.args = {**node['variables']}
                    nodes.append([node_id, node_instance])
                    nodes_mapping[node_id] = node_instance

            # TODO: kind of wierd to do the connection logic here, I should let the pipeline handle
            if "CONNECTIONS" in data:
                for connection in data["CONNECTIONS"]:
                    parent_id, parent_terminal = connection[0].split('.')
                    child_id, child_terminal = connection[1].split('.')
                    parent = nodes_mapping[parent_id]
                    child = nodes_mapping[child_id]
                    connections.append([(parent, parent_terminal), (child, child_terminal)])

            if "GLOBALS" in data:
                for global_var in data["GLOBALS"]:
                    print(global_var)

            return nodes, connections, global_vars