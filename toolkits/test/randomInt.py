from consecution import Node
import random

class randomInt(Node):
    def begin(self):
        # This sets up whatever state you want to exist before the
        # node begins processing any data.  You can think of it as an
        # init method that runs just before the node starts processing.
        # In this example, we initialize a simple counter
        self.counter = 0
        self.counterMax = 0
        self.min = 0
        self.max = 100

    def process(self, item):
        # This is the method that defines the processing you want to perform
        # on every item the node processes.  You can place whatever logic
        # you want here, including calls the the .push() method.
        # In this example, we update the counter and push the item
        # downstream.
        if self.counter < self.counterMax:
            self.counter += 1
            self.push(random.randint(self.min,self.max))
        else:
            self.end(self)

    def end(self):
        # This method is called right after all items are processed.
        # This happens  when the iterator being consumed by the pipeline
        # is exhausted.  At that point the .end() methods of all nodes
        # in the pipeline are called.  This is a good place for you to
        # push any summary information downstream.
        # In this example we push the results of our counter
        self.push()

    def reset(self):
        # A pipeline can be reused and reset back to its initial condition.
        # It does this by calling the .reset() method of all its member
        # nodes.  You can place whatever code you want here to reset your
        # node to its initial state.
        # In this example, we simply reset the counter.
        self.counter = 0
