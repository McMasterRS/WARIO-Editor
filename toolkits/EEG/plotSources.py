from pipeline.Node import Node
import mne

class plotSources(Node):
    def __init__(self, name, params):
        super(plotSources, self).__init__(name, params)

    def process(self):

        inst = self.args["Data"]
        ica = self.args["ICA Solution"]
        fig = ica.plot_sources(inst, show = False)
        if self.parameters["showGraph"] == True:
            fig.show()