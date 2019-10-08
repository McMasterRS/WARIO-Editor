from pipeline.Node import Node
from parselmouth.praat import call
from toolkits.Voicelab.VoicelabNode import VoicelabNode

###################################################################################################
# MEASURE FORMANTS NODE
# WARIO pipeline node for measuring the formants of a voice
###################################################################################################
# PIPELINE ARGUMENTS
# 'voice' :
# 'time step':
# 'max number of formants':
# 'window length(s): 
# 'pre emphasis from'
# 'pitch floor'
# 'pitch ceiling'
# 'method': Option tuple for the praat algorithm to use, 0 = selected value, 1 = available options
# 'maximum formant': Maximum formant. Default is to dynamically calculate during runtime
###################################################################################################
# RETURNS
###################################################################################################

class MeasureFormantNode(VoicelabNode):

    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)

        self.args = {
            'time step': 0.0025, # a zero value is equal to 25% of the window length
            'max number of formants': 5,  # always one more than you are looking for
            'window length(s)': 0.025,
            'pre emphasis from': 50,
            'pitch floor': 50,
            'pitch ceiling': 500,
            'method': ('formants_praat_manual', ['formants_praat_manual', 'sweep']),
            'maximum formant': self.formant_max,
        }
    ###############################################################################################
    # process: WARIO hook called once for each voice file.
    ###############################################################################################

    def process(self):
        'formants'

        sound = self.args['voice']

        pitch = call(sound, "To Pitch", 0.0, 50, 500)  # check pitch to set formant settings
        mean_f0 = call(pitch, "Get mean", 0, 0, "Hertz")

        formant_object = call(sound,
            "To Formant (burg)",
            self.args['time step'],
            self.args['max number of formants'],
            self.args['maximum formant'](sound),
            self.args['window length(s)'],
            self.args['pre emphasis from']
        )

        f1_mean = call(formant_object, "Get mean", 1, 0, 0, 'Hertz')
        f2_mean = call(formant_object, "Get mean", 2, 0, 0, 'Hertz')
        f3_mean = call(formant_object, "Get mean", 3, 0, 0, 'Hertz')
        f4_mean = call(formant_object, "Get mean", 4, 0, 0, 'Hertz')

        f1_median = call(formant_object, "Get quantile", 1, 0, 0, "Hertz", 0.5)
        f2_median = call(formant_object, "Get quantile", 2, 0, 0, "Hertz", 0.5)
        f3_median = call(formant_object, "Get quantile", 3, 0, 0, "Hertz", 0.5)
        f4_median = call(formant_object, "Get quantile", 4, 0, 0, "Hertz", 0.5)

        return {
            'Formant Medians': [f1_median, f2_median, f3_median, f4_median],
            'Formant Means': [f1_mean, f2_mean, f3_mean, f4_mean],
        }

    def formant_max(self, voice):

        pitch = call(voice, "To Pitch", 0.0, 50, 500)  # check pitch to set formant settings
        mean_f0 = call(pitch, "Get mean", 0, 0, "Hertz")

        if 170 <= mean_f0 <= 300:
            max_formant = 5500

        elif mean_f0 < 170:
            max_formant = 5000

        else:
            max_formant = 8000

        return max_formant