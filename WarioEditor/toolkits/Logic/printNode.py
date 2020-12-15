from wario import Node

class printNode(Node):

    def __init__(self, name, params):   
        super(printNode, self).__init__(name, params)
        
        
    def process(self):
    
        # Hide any unconnected bits
        for i in range(1, 5):
            if "In {0}".format(i) not in self.args.keys():
                self.args["In {0}".format(i)] = ""
                
            if self.args["In {0}".format(i)] == True:
                self.args["In {0}".format(i)] = "1"
            elif self.args["In {0}".format(i)] == False:
                self.args["In {0}".format(i)] = "0"
                
        print(self.args["In 4"] + self.args["In 3"] + self.args["In 2"] + self.args["In 1"])
        