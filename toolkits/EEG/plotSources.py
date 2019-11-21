from pipeline.Node import Node
import mne
import pickle
import matplotlib.pyplot as plt

class plotSources(Node):
    def __init__(self, name, params):
        super(plotSources, self).__init__(name, params)
        
        if self.parameters["saveGraph"] is not None:
            assert(self.parameters["saveGraph"] is not ""), "ERROR: Plot Sources node set to save but no filename has been given. Please update the node settings and re-run"

    def process(self):

        inst = self.args["Data"]
        ica = self.args["ICA Solution"]
        fig = ica.plot_sources(inst, show = False)
            
        if self.parameters["saveGraph"] is not None:
        
            if "globalSaveStart" in self.parameters.keys():
                f = self.parameters["globalSaveStart"] + self.global_vars["Output Filename"] + self.parameters["globalSaveEnd"]
            else:
                f = self.parameters["saveGraph"]
                
            type = f.split(".")[-1]
            if type == "png":
                fig.savefig(f, format = "png")
            elif type == "pdf":
                fig.savefig(f, format = "pdf")
            elif type == "pkl":
                pickle.dump(fig, open(f, "wb"))
                    
        if self.parameters["showGraph"] == True:
            fig.show()
        else:
            plt.close(fig)