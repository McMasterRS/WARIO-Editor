from parselmouth.praat import call
from VoicelabWizard.AutomaticParams import *

from toolkits.Voicelab.MeasureNode import *
from toolkits.Voicelab.ManipulateNode import *
from toolkits.Voicelab.VisualizeNode import *

# List of default settings matching at least one of the available functions
default_settings = {

    'Measure Pitch': {
        'Algorithm': ('To Pitch (ac)', ['To Pitch (cc)']),
        'Time Step': 0,
        'Max Number of Candidates': 15,
        'Very Accurate': ('no', ['yes']),
        'Silence Threshold': 0.03,
        'Voicing Threshold': 0.45,
        'Octave Cost': 0.01,
        'Octave Jump Cost': 0.35,
        'Voiced Unvoiced Cost': 0.14,
        'Ceiling': pitch_ceiling,
        'Floor': pitch_floor
    },
    'Measure Harmonicity': {
        'Floor': 50,
        'Ceiling': 500,
        'Algorithm': ('To Harmonicity (cc)', ['To Harmonicity (ac)']),
        'Time Step': 0.01,
        'Silence Threshold': 0.1,
        'Periods per Window': 1.0
    },
    'Measure Jitter': {
        'Floor': 50,
        'Ceiling': 500,
        'Start Time': 0,
        'End Time': 0,
        'Shortest Period': 0.0001,
        'Longest Period': 0.02,
        'Maximum Period Factor': 1.3
    },
    'Measure Shimmer': {
        'floor': 50,
        'ceiling': 500,
        'start_time': 0,
        'end_time': 0,
        'shortest_period': 0.0001,
        'longest_period': 0.02,
        'maximum_period_factor': 1.3,
        'maximum_amplitude': 1.6
    },
    'Measure Formants': {
        'Time Step': 0, # a zero value is equal to 25% of the window length
        'Max Number of Formants': 5,  # always one more than you are looking for
        'Maximum Formant': 5500,
        'Window Length(s)': 0.025,
        'Pre Emphasis From': 50,
        'Pitch Floor': 50,
        'Pitch Ceiling': 500,
        'Means': formant_means,
        'Max': formant_max
    },
    'Manipulate Pitch': {
        'Unit': 'ERB',
        'Factor': -0.5
    }

}

# List of all available operations the user can perform as well as their associated function node
avialable_functions = {

    'Measure Pitch': MeasurePitchNode('Measure Pitch'),
    'Measure Intensity': MeasureIntensityNode('Measure Intensity'),
    'Measure Harmonicity': MeasureHarmonicityNode('Measure Harmonicity'),
    'Measure Jitter': MeasureJitterNode('Measure Jitter'),
    'Measure Shimmer': MeasureShimmerNode('Measure Shimmer'),
    'Measure Formants': MeasureFormantNode('Measure Formants'),
    'Measure Jitter PCA': MeasureJitterPCANode('Measure Jitter PCA'),
    'Measure Shimmer PCA': MeasureShimmerPCANode('Measure Shimmer PCA'),
    'Measure Formant PCA' : MeasureFormantPCANode('Measure Formant PCA'),
    'Measure Vocal Tract Estimates': MeasureVocalTractEstimatesNode('Measure Vocal Tract Estimates'),

    'Manipulate Pitch': ManipulatePitchNode('Manipulate Pitch'),
    'Manipulate Formants': ManipulateFormantsNode('Manipulate Formants'),
    'Manipulate Gender and Age': ManipulateGenderAgeNode('Manipulate Gender and Age'),

    # 'Visualize Pitch': VisualizePitchNode(),
    # 'Visualize Intensity': VisualizeIntensityNode(),
    # 'Visualize Formants': VisualizeFormantNode(),

}

# List of default operations that will be performed when there is no custom configuration
default_functions = [

    'Measure Pitch',
    'Measure Shimmer',
    'Measure Jitter',
    'Manipulate Pitch',
    'Visualize Pitch',

]