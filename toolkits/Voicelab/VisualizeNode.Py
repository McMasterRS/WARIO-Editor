from pipeline.Node import Node
import numpy as np
import seaborn as sns
import parselmouth
from parselmouth.praat import call
import matplotlib.pyplot as plt

class SaveVoiceSpectrogram(Node):
    def process(self):

        colour_map = self.args['colour']
        voice = self.args['voice']
        pitch = self.args['pitch'] if ('pitch' in self.args) else False
        intensity = self.args['intensity'] if ('intensity' in self.args) else False
        formants = self.args['formants'] if ('formants' in self.args) else False
        
        spectrogram = self.args['voice'].to_spectrogram(window_length=self.args['window_length'], maximum_frequency=8000)
        
        ## Plot Base Spectrogram ##
        fig, host = plt.subplots()
        x, y = spectrogram.x_grid(), spectrogram.y_grid()
        sg_db = 10 * np.log10(spectrogram.values)
        vgmin_value = sg_db.max() - 70
        host.pcolormesh(x, y, sg_db, vmin=vgmin_value, cmap=colour_map)
        host.set_ylim([spectrogram.ymin, spectrogram.ymax])
        host.set_xlabel("Time [s]", labelpad=15)
        host.set_ylabel("Frequency [Hz]", labelpad=15)
        host.yaxis.label.set_color('w')
        host.set_xlim([self.args['voice'].xmin, self.args['voice'].xmax])
        sns.set()
        fig.set_dpi(250)
        fig.set_size_inches(9, 4)

        ## Overlay Pitch ##

        ## Overlay Intensity ##

        ## Overlay Formants ##

        plt.show()

        return {
            "plot": plt
        }

class PlotPitch(Node):
    def process(self):
        # use the provided plot if one is provided, otherwise create a new one
        pitch = self.args['pitch']
        intensity = self.args['intensity']
        figure, host = self.args['figure'], self.args['host'] if ('figure' in self.args and 'host' in self.args) else plt.subplots()
        axis = host.twinx()
        pitch_values = pitch.selected_array['frequency']
        sample_times = pitch.xs()

        for i, time in enumerate(sample_times):
            intensity.values.T[intensity.values.T < 50] = np.nan
            intensity_value = call(intensity, "Get value at time", time, "cubic")
            if intensity_value < 50:
                pitch_values[i] = 0

        pitch_values[pitch_values == 0] = np.nan
        axis.plot(pitch.xs(), pitch_values, linestyle='-', color='k', linewidth=6)
        axis.plot(pitch.xs(), pitch_values, linestyle='-', color='w', linewidth=5)
        axis.plot(pitch.xs(), pitch_values, linestyle='-', color='b', linewidth=4)
        axis.grid(False)
        pitch_max = 500
        axis.set_ylim(0, pitch_max)
        axis.set_ylabel("Fundamental frequency [Hz]")
        axis.yaxis.label.set_color('b')

        return {
            'figure': figure,
            'host': host,
            'axis': axis,
        }

class PlotIntensity(Node):
    def process(self):
        intensity = self.args['intensity']
        figure, host = self.args['figure'], self.args['host'] if ('figure' in self.args and 'host' in self.args) else plt.subplots()
        axis = host.twinx()

        intensity.values.T[intensity.values.T < 50] = np.nan
        axis.plot(intensity.xs(), intensity.values.T, linewidth=3, color='k')
        axis.plot(intensity.xs(), intensity.values.T, linewidth=2, color='w')
        axis.plot(intensity.xs(), intensity.values.T, linewidth=1, color='g')
        axis.grid(False)
        plt.ylim(50)
        axis.set_ylabel("Intensity [dB]")
        axis.yaxis.label.set_color('g')
        return {
            'figure': figure,
            'host': host,
            'intensity': intensity
        }

class PlotFormants(Node):
    def process(self):
        'generate a new axis for these formants and plot them to a new or provided grid'

        formants = self.args['formants']
        intensity = self.args['intensity']
        figure, host = self.args['figure'], self.args['host'] if ('figure' in self.args and 'host' in self.args) else plt.subplots()
        axis = host.twinx()
        sample_times = formants.xs()

        for i in range(4):  # How many formants do you want?
            formant_values = call(formants, "To Matrix", i + 1).values[0, :]
            for j, time in enumerate(sample_times):
                intensity_value = call(intensity, "Get value at time", time, "cubic")
                if intensity_value < 50:
                    formant_values[j] = 0

            formant_values[formant_values == 0] = np.nan
            axis.scatter(sample_times, formant_values, c='w', linewidth=3, marker='o', s=1)
            axis.scatter(sample_times, formant_values, c='r', linewidth=1, s=1)
            axis.grid(False)
            return {
                'figure': figure,
                'host': host,
                'axis': axis,
                'formants': formants
            }

class PlotSpectrogram(Node):
    def process(self):

        voice = self.args['voice']
        window_length = self.args['window_length'] if 'window_length' in self.args else 0.05
        colour_map = self.args['colour'] if 'colour' in self.args else 'binary'
        figure, host = (self.args['figure'], self.args['host']) if ('figure' in self.args and 'host' in self.args) else plt.subplots()

        spectrogram = voice.to_spectrogram(window_length=window_length, maximum_frequency=8000)
        x, y = spectrogram.x_grid(), spectrogram.y_grid()

        sg_db = 10 * np.log10(spectrogram.values)
        vgmin_value = sg_db.max() - 70
        host.pcolormesh(x, y, sg_db, vmin=vgmin_value, cmap=colour_map)
        host.set_ylim([spectrogram.ymin, spectrogram.ymax])
        host.set_xlabel("Time [s]", labelpad=15)
        host.set_ylabel("Frequency [Hz]", labelpad=15)
        host.yaxis.label.set_color('w')
        host.set_xlim([self.args['voice'].xmin, self.args['voice'].xmax])
        sns.set()
        figure.set_dpi(250)
        figure.set_size_inches(9, 4)

        return {
            'figure': figure,
            'host': host,
            'spectrogram': spectrogram
        }

class ShowVoicePlot(Node):
    def process(self):
        plt.show()

class SaveVoicePlot(Node):
    def process(self):
        pass

# SaveVoiceSpectrogram()
#     args = {
#         'colour': 'binary',
#         'voice': parselmouth.Sound('./test_voices/f4047_ah.wav'),
#         'save_location': '/spectrograms/f4047_ah.png',
#         'window_length': 0.05
#     }
