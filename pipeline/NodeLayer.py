from pipeline.TaskFactory import TaskFactory
import json

NODZ_SAVE = "./pipeline/saves/sample.json"

class NodeLayer():

    def __init__(self):
        with open(NODZ_SAVE, 'r') as f:
            d = json.load(f)
            self.data = d

    # TODO: Assumes a well formatted json file, should validate this.
    # TODO: Much better name for this function
    def parse_nodz(self):
        nodz_json = self.data
        tasks = {}
        connections = []
        node_types = {}

        for nod in nodz_json["NODES"]:
            #TODO: this is not how it should be done, the saves for nodz are formated file.py. we dont want the py
            node_types[nod] = nodz_json["NODES"][nod]["file"].split(".")[0]

        print(list(node_types.values()))

        task_factory = TaskFactory(list(node_types.values()))
        for nod in nodz_json["NODES"]:
            tasks[nod] = task_factory.create_task(node_types[nod], nod)
        for connection in nodz_json["CONNECTIONS"]:
            connections.append([tasks[connection[0].split(".")[0]], tasks[connection[1].split(".")[0]]])
    
        return [tasks, connections]