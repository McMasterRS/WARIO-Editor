from pipeline.Node import Node
import mne

class mergeLists(Node):
    
    def __init__(self, name, params):
        super(mergeLists, self).__init__(name, params)
    
    def process(self):
        
        list = []
        
        for i in range(4):
            if "List {0}".format(i) in self.args.keys():
                list.append(self.args["List {0}".format(i)])
                
        if self.parameters["deleteDuplicates"] == True:
            list = list(dict.fromkeys(list))
                
        return {"Merged List" : list}
    