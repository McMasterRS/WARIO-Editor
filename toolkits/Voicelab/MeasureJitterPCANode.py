from pipeline.Node import Node
from parselmouth.praat import call
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

import pandas as pd

from toolkits.Voicelab.VoicelabNode import VoicelabNode
from toolkits.Voicelab.MeasureJitterNode import MeasureJitterNode

###################################################################################################
# MEASURE JITTER PCA NODE
# WARIO pipeline node for performing principle component analysis on the jitter of a voice.
###################################################################################################
# ARGUMENTS
# 'voice'   : sound file generated by parselmouth praat
###################################################################################################
# RETURNS
###################################################################################################

class MeasureJitterPCANode(VoicelabNode):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # this node can construct it's own node for measuring jitter if none is attached
        # this means that it uses the same functionality as all other measurement nodes
        # without having to specify dependancies
        # the default getter functions are linked to the internal measure jitter node
        # constant variables can be passed in, in which case these will not run
        self.args = {
            'local_jitter': lambda voice: self.measure_jitter(voice)['local_jitter'],
            'localabsolute_jitter': lambda voice: self.measure_jitter(voice)['localabsolute_jitter'],
            'rap_jitter': lambda voice: self.measure_jitter(voice)['rap_jitter'],
            'ppq5_jitter': lambda voice: self.measure_jitter(voice)['ppq5_jitter'],
            'ddp_jitter': lambda voice: self.measure_jitter(voice)['ddp_jitter'],
        }

        self.cached = {}

    def process(self):

        voice = self.args['voice']

        local_jitter =  self.args['local_jitter'](voice)
        local_abs_jitter =  self.args['localabsolute_jitter'](voice),
        rap_jitter =  self.args['rap_jitter'](voice),
        ppq5_jitter =  self.args['ppq5_jitter'](voice),
        ddp_jitter =  self.args['ddp_jitter'](voice)
        
        jitter_values = {
            'local_jitter': local_jitter,
            'local_abs_jitter': local_abs_jitter,
            'rap_jitter': rap_jitter,
            'ppq5_jitter': ppq5_jitter,
            'ddp_jitter': ddp_jitter
        }

        jitter_df = pd.DataFrame(data=jitter_values, index=[0])

        # df = self.args['df'] # dataframe
        try:
            # z-score the Jitter measurements
            measures = ['localJitter', 'localabsoluteJitter', 'rapJitter', 'ppq5Jitter', 'ddpJitter']
            # x = df.loc[:, measures].values
            x = jitter_df
            x = StandardScaler().fit_transform(x)

            # Run the PCA
            pca = PCA(n_components=1)
            principal_components = pca.fit_transform(x)
            jitter_pca_df = pd.DataFrame(data=principal_components, columns=['JitterPCA'])

            return {
                'jitter_pca_df': jitter_pca_df
            }

        except:
            print('Jitter PCA failed.  Please check your data') # todo make this an error message
            return {
                'jitter_pca_df': None
            }
        
    # I want some way to run this node without needing any upstream nodes (except loading a voice)
    # but I also want to optionally pass these values in. This may conflict with our desire to keep
    # each node suitably atomic in it's behaviour
    def measure_jitter(self, voice):
        if voice not in self.cached:
            measure_jitter = MeasureJitterNode('Measure Shimmer')
            measure_jitter.args['voice'] = voice
            results = measure_jitter.process()
            self.cached = { voice: results }
            return results
        return self.cached[voice]


        # if voice not in self.cached:

        #     # create a temporary node to measure jitter
        #     measure_jitter_node = MeasureJitterNode('MeasureJitter')
        #     measure_jitter_node.args['voice'] = voice
        #     results = measure_jitter_node.process()

        #     # if these are properties measured by the jitter node
        #     local_jitter = results['local_jitter'] if 'local_jitter' in results else None
        #     local_absolute_jitter = results['local_absolute_jitter'] if 'local_absolute_jitter' in results else None
        #     rap_jitter = results['rap_jitter'] if 'rap_jitter' in results else None
        #     ppq5_jitter = results['ppq5_jitter'] if 'ppq5_jitter' in results else None
        #     ddp_jitter = results['ddp_jitter'] if 'ddp_jitter' in results else None

        #     # we want this function to only run once no matter how many parameters we measure
        #     # so we cache the results and check them in each attributes getter
        #     self.cached = {}
        #     self.cached[voice] = {
        #         'local_jitter': local_jitter,
        #         'local_absolute_jitter': local_absolute_jitter,
        #         'rap_jitter': rap_jitter,
        #         'ppq5_jitter': ppq5_jitter,
        #         'ddp_jitter': ddp_jitter
        #     }

        # return self.cached[voice]