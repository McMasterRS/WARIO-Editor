## TODO: Not intended to be the final node, only while we are breaking out functionality
from pipeline.Node import Node
import numpy as np
import seaborn as sns

class VisualizeVoiceSpectrogram(Node):

    def process(self):

        sound = self.args['sound']
        window_length = self.args['window_length']
        dynamic_range = self.args['dynamic_range']
        host = self.args['host']
        fig = self.args['fig']
        colour_scheme = self.args['colour_scheme']
        pre_emphasized_voice = sound.copy().pre_emphasize()

        spectrogram = pre_emphasized_voice.to_spectrogram(window_length=window_length, maximum_frequency=8000)
        x, y = spectrogram.x_grid(), spectrogram.y_grid()
        sg_db = 10 * np.log10(spectrogram.values)
        vgmin_value = sg_db.max() - dynamic_range
        host.pcolormesh(x, y, sg_db, vmin=vgmin_value, cmap=colour_scheme)
        host.set_ylim([spectrogram.ymin, spectrogram.ymax])
        host.set_xlabel("Time [s]", labelpad=15)
        host.set_ylabel("Frequency [Hz]", labelpad=15)
        host.yaxis.label.set_color('w')
        host.set_xlim([sound.xmin, sound.xmax])
        sns.set()
        fig.set_dpi(250)
        fig.set_size_inches(9, 4)
        
        return {
            'figure': fig
        }