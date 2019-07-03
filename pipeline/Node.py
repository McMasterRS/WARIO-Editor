class Node():
    """ abstract node class. this describes a single operational function in our process pipeline """

    def begin(self):
        pass

    def process(self):
        pass
    
    def end(self):
        pass

    def reset(self):
        pass