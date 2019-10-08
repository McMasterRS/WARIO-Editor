from pipeline.Node import Node
from parselmouth.praat import call
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

import pandas as pd

from toolkits.Voicelab.VoicelabNode import VoicelabNode
from toolkits.Voicelab.MeasureShimmerNode import MeasureShimmerNode

###################################################################################################
# MEASURE SHIMMER PCA NODE
# WARIO pipeline node for performing principle component analysis on a the shimmer in a voice.
###################################################################################################
# ARGUMENTS
# 'voice'   : sound file generated by parselmouth praat
###################################################################################################
# RETURNS
###################################################################################################

class MeasureShimmerPCANode(VoicelabNode):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cached = {}

        # The default values are generated by measuring the jitter of the voice
        self.args = {
            'Local Shimmer': lambda voice: self.measure_shimmer(voice)['local_shimmer'],
            'Local DB Shimmer': lambda voice: self.measure_shimmer(voice)['localdb_shimmer'],
            'APQ3 Shimmer': lambda voice: self.measure_shimmer(voice)['apq3_shimmer'],
            'APQP5 Shimmer': lambda voice: self.measure_shimmer(voice)['aqpq5_shimmer'],
            'APQ11 Shimmer': lambda voice: self.measure_shimmer(voice)['apq11_shimmer'],
            'DDA Shimmer': lambda voice: self.measure_shimmer(voice)['dda_shimmer'],
        }
        
    ###############################################################################################
    # process: WARIO hook called once for each voice file.
    ###############################################################################################

    def process(self):

        voice = self.args['voice']
        local_shimmer = self.args['Local Shimmer'](voice)
        localdb_shimmer = self.args['Local DB Shimmer'](voice)
        apq3_shimmer = self.args['APQ3 Shimmer'](voice)
        aqpq5_shimmer = self.args['APQP5 Shimmer'](voice)
        apq11_shimmer = self.args['APQ11 Shimmer'](voice)
        dda_shimmer = self.args['DDA Shimmer'](voice)

        shimmer_values = {
            'local_shimmer': local_shimmer,
            'localdb_shimmer': localdb_shimmer,
            'apq3_shimmer': apq3_shimmer,
            'aqpq5_shimmer': aqpq5_shimmer,
            'apq11_shimmer': apq11_shimmer,
            'dda_shimmer': dda_shimmer,
        }

        shimmer_values = pd.DataFrame(data=shimmer_values, index=[0])

        try:
            # z-score the Shimmer measurements
            x = shimmer_values
            x = StandardScaler().fit_transform(x)
            # Run the PCA
            pca = PCA(n_components=1)
            principal_components = pca.fit_transform(x)
            shimmer_pca_df = pd.DataFrame(data=principal_components, columns=['ShimmerPCA'])
            return shimmer_pca_df
        except:
            print('Shimmer PCA failed.  Please check your data') # todo make this an error message

    def measure_shimmer(self, voice):
        if voice not in self.cached:
            measure_shimmer = MeasureShimmerNode('Measure Shimmer')
            measure_shimmer.args['voice'] = voice
            results = measure_shimmer.process()
            self.cached = { voice: results }
            return results
        return self.cached[voice]
