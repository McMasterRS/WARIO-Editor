from pipeline.Node import Node
import matplotlib.pyplot as plt

class BasicMatplotOutputNode(Node):

    def __init__(self, node_id):
        super(BasicMatplotOutputNode, self).__init__(node_id)
        self.x = []
        self.y = []
        self.event_callbacks = {
            "Row End": self.plot
        }

    def process(self):

        x = self.args['X']
        y = self.args['Y']

        self.x.append(x)
        self.y.append(y)

    def plot(self, event_id, event_data):
        fig, ax = plt.subplots()
        ax.plot(self.x, self.y)
        ax.grid()
        fig.savefig("test.png")
        plt.show()
