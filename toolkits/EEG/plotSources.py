from pipeline.Node import Node
import mne
import pickle

class plotSources(Node):
    def __init__(self, name, params):
        super(plotSources, self).__init__(name, params)
        
        if self.parameters["saveGraph"] is not None:
            assert(self.parameters["saveGraph"] is not ""), "ERROR: Plot Sources node set to save but no filename has been given. Please update the node settings and re-run"

    def process(self):

        inst = self.args["Data"]
        ica = self.args["ICA Solution"]
        fig = ica.plot_sources(inst, show = False)
        if self.parameters["showGraph"] == True:
            fig.show()
            
        if self.parameters["saveGraph"] is not None:
            f = self.parameters["saveGraph"]
            if f is not None:
                type = f.split(".")[-1]
                if type == "png":
                    fig.savefig(f, format = "png")
                elif type == "pdf":
                    fig.savefig(f, format = "pdf")
                elif type == "pkl":
                    pickle.dump(fig, open(f, "wb"))