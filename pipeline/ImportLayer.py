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

        tasks = {}
        task_types = {}
        connections = {}

        # Populates the types of tasks, key = task type string, value = the file name
        for nod in data["NODES"]:

            task_name = nod
            task_signature = {
                "in": [],
                "out": [],
                "paramaters": None,
                "type": None
            }

            for attribute in data["NODES"][nod]["attributes"]:
                if attribute["socket"]:
                    task_signature["out"].append(attribute["name"])
                if attribute["plug"]:
                    task_signature["in"].append(attribute["name"])
            
            task_signature["paramaters"] = data["NODES"][nod]["variables"] # silly name mismatch here, should standardize the name of things
            task_signature["type"] = data['NODES'][nod]["type"]
            tasks[task_name] = task_signature

            task_type = data["NODES"][nod]["type"]
            file_location = data["NODES"][nod]["file"].split(".")[0] #TODO: The nodz saves are formated 'file'.py. we dont want the py
            task_types[task_type] = file_location

            connections[nod] = {}

        # Populates the connections
        for connection in data["CONNECTIONS"]:

            parent_name = connection[0].split(".")[0]
            parent_attribute = connection[0].split(".")[1]
            child_name = connection[1].split(".")[0]
            child_attribute = connection[1].split(".")[1]

            connections[parent_name][parent_attribute] = [child_name, child_attribute]
            connections[child_name][child_attribute] = [child_name, child_attribute]

        return [task_types, tasks, connections]