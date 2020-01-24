from .NodeFactory import NodeFactory
from .NodzInterface import NodzInterface
from .Pipeline import Pipeline
from blinker import signal

import traceback
import threading

class PipelineThread(threading.Thread):

    def __init__(self, file):
        threading.Thread.__init__(self)
        self.file = file

    def run(self):  
        try:
            # Extract relevant info from the JSON
            nodes, connections, globals = NodzInterface.load(self.file)

            # Build the pipeline graph
            pipeline = Pipeline(global_vars = globals)

            for node in nodes:
                pipeline.add(node[1])
                
            for conn in connections:
                pipeline.connect(parent = conn[0], child = conn[1])

            pipeline.start()
            
        # Catches any runtime errors and prints to console
        # Lets you debug the pipeline nodes if they crash
        except Exception:
            traceback.print_exc()