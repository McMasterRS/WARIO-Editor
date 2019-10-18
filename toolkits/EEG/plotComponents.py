from pipeline.Node import Node
import mne

class plotComponents(Node):
    def __init__(self, name, params):
        super(plotComponents, self).__init__(name, params)

    def process(self):

        ica = self.args["ICA Solution"]
        fig = ica.plot_components(show = False)
        if self.parameters["showGraph"] == True:
            fig.show()