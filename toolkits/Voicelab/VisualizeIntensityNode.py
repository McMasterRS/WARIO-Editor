from pipeline.Node import Node
import numpy as np
import seaborn as sns
import parselmouth
from parselmouth.praat import call
import matplotlib.pyplot as plt

from toolkits.Voicelab.VoicelabNode import VoicelabNode
from toolkits.Voicelab.MeasureIntensityNode import MeasureIntensityNode


###################################################################################################
# VISUALIZE INTENSITY NODE
# WARIO pipeline node for visualizing the intensity of a voice on a plot.
###################################################################################################
# ARGUMENTS
# 'voice'   : sound file generated by parselmouth praat
###################################################################################################
# RETURNS
###################################################################################################


class VisualizeIntensityNode(VoicelabNode):

    def process(self):

        figure = self.args['figure']
        voice = self.args['voice']
        host = figure.axes[0]
        axis = host.twinx()

        intensity = voice.to_intensity()
        intensity.values.T[intensity.values.T < 50] = np.nan
        axis.plot(intensity.xs(), intensity.values.T, linewidth=3, color='k')
        axis.plot(intensity.xs(), intensity.values.T, linewidth=2, color='w')
        axis.plot(intensity.xs(), intensity.values.T, linewidth=1, color='g')
        axis.grid(False)
        plt.ylim(50)
        axis.set_ylabel("Intensity [dB]", labelpad=10)
        axis.yaxis.label.set_color('g')
        return {
            'figure': figure,
            'host': host,
            'intensity': intensity
        }