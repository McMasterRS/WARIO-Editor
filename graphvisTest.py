from graphviz import Digraph
import os, json
os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/'

def GenerateGraph(file_location, save_location):

    dot = Digraph()

    with open(file_location, 'r') as f:
        data = json.load(f)

        if "NODES" in data:
            for node_id in data["NODES"]:
                dot.node(node_id, data["NODES"][node_id]["name"])
            
        if "CONNECTIONS" in data:
            conList = []
            conNames = []
            
            for conn in data["CONNECTIONS"]:
                c1 = conn[0].split(".")[0]
                c2 = conn[1].split(".")[0]
                name = conn[0].split(".")[1]
                
                found = False
                for i in range(len(conList)):
                    if conList[i][0] == c1 and conList[i][1] == c2:
                        conNames[i] += "/" + name
                        found = True
                        
                if found == False:
                    conList.append([c1, c2])
                    conNames.append(name)              
                    
            for i, item in enumerate(conList):
                dot.edge(item[0], item[1], label = conNames[i])

    dot.render(saveLocation, view=True)