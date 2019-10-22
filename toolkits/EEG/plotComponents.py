from pipeline.Node import Node
import mne
import pickle

class plotComponents(Node):
    def __init__(self, name, params):
        super(plotComponents, self).__init__(name, params)
        
        if self.parameters["saveGraph"] is not None:
            assert(self.parameters["saveGraph"] is not ""), "ERROR: Plot Components node set to save but no filename has been given. Please update the node settings and re-run"

    def process(self):

        ica = self.args["ICA Solution"]
        fig = ica.plot_components(show = False)[0]
        if self.parameters["showGraph"] == True:
            fig.show()
                
        if self.parameters["saveGraph"] is not None:
            f = self.parameters["saveGraph"]
            type = f.split(".")[-1]
            if type == "png":
                fig.savefig(f, format = "png")
            elif type == "pdf":
                fig.savefig(f, format = "pdf")
            elif type == "pkl":
                pickle.dump(fig, open(f, "wb"))