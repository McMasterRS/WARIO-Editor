from TaskFactory import TaskFactory
import json

NODZ_SAVE = "./sample.json"
NODZ_CONFIG = ""
TASKS = TaskFactory()

class NodeLayer():
    def __init__():
        pass
    # def read_nodz(self):
    #     with open(NODZ_FILE, 'r') as f:
    #         d = json.load(f)
    #         self.parse_nodz(d)

    # # TODO: Assumes a well formatted json file, should validate this.
    # # TODO: Much better name for this function
    # def parse_nodz(self, nodz_json):
    #     tasks = []

    #     for nod in nodz_json["NODES"]:
    #         self.nod_to_task(nod)

    #     for connection in nodz_json["CONNECTIONS"]:
    #         self.connect(self.tasks[connection[0].split(".")[0]], self.tasks[connection[1].split(".")[0]])

    # def nod_to_task(self, nod):
    #     return Task()