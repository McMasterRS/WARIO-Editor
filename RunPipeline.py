from pipeline.NodeFactory import NodeFactory
from pipeline.NodzInterface import NodzInterface
from pipeline.Pipeline import Pipeline
from PyQt5.QtCore import *
import traceback
import sys

def runPipeline(file):
    try:
        nodes, connections, globals = NodzInterface.load(file)

        pipeline = Pipeline(global_vars = globals)

        for node in nodes:
            pipeline.add(node[1])
            
        for conn in connections:
            pipeline.connect(parent = conn[0], child = conn[1])
            
        pipeline.start()
               
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    runPipeline(sys.argv[1])
    

    


