from parselmouth.praat import call
from VoicelabWizard.AutomaticParams import *

import toolkits.Voicelab as Voicelab

# from toolkits.Voicelab.MeasureNode import *
# from toolkits.Voicelab.ManipulateNode import *
# from toolkits.Voicelab.VisualizeNode import *

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
        'Floor': 50,
        'Ceiling': 500,
        'Start Time': 0,
        'End Time': 0,
        'Shortest Period': 0.0001,
        'Longest Period': 0.02,
        'Maximum Period Factor': 1.3,
        'maximum Amplitude': 1.6
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
# Human readable mapping
avialable_functions = {

    'Measure Duration': Voicelab.MeasureDurationNode('Measure Duration'),
    'Measure Pitch': Voicelab.MeasurePitchNode('Measure Pitch'),
    'Measure Harmonicity': Voicelab.MeasureHarmonicityNode('Measure Harmonicity'),
    'Measure Jitter': Voicelab.MeasureJitterNode('Measure Jitter'),
    'Measure Shimmer': Voicelab.MeasureShimmerNode('Measure Shimmer'),
    'Measure Formants': Voicelab.MeasureFormantNode('Measure Formants'),

    # These have additional requirements. The proceeding outputs will be passed to the final node

    # Measure jitter, then perform PCA on the results
    'Measure Jitter PCA': Voicelab.MeasureJitterPCANode('Measure Jitter PCA'),
    # Measure shimmer, then perform PCA on the results
    'Measure Shimmer PCA': Voicelab.MeasureShimmerPCANode('Measure Shimmer PCA'),
    # Measure formants, then perform PCA on the results
    'Measure Formant PCA' : Voicelab.MeasureFormantPCANode('Measure Formant PCA'),
    # Measure the formants, then estimate the vocal tract properties based on them
    'Measure Vocal Tract Estimates': Voicelab.MeasureVocalTractEstimatesNode('Measure Vocal Tract Estimates'),

    'Manipulate Pitch': Voicelab.ManipulatePitchNode('Manipulate Pitch'),
    'Manipulate Formants': Voicelab.ManipulateFormantsNode('Manipulate Formants'),
    'Manipulate Gender and Age': Voicelab.ManipulateGenderAgeNode('Manipulate Gender and Age'),

    'Visualize Pitch': Voicelab.VisualizePitchNode('Visualize Pitch'),
    'Visualize Intensity':Voicelab.VisualizeIntensityNode('Visualize Intensity'),
    'Visualize Formants':Voicelab.VisualizeFormantNode('Visualize Formants'),
    'Visualize Voice': Voicelab.VisualizeVoiceNode('Visualize Voice')
}

# List of default functions that will be performed.
default_functions = [

    # 'Manipulate Formants',
    # 'Manipulate Gender and Age',
    # 'Manipulate Pitch',

    # 'Measure Duration',
    # 'Measure Formants',
    # 'Measure Formant PCA',
    # 'Measure Harmonicity',
    # 'Measure Jitter',
    # 'Measure Jitter PCA',
    'Measure Pitch',
    # 'Measure Formants',
    # 'Measure Shimmer',
    # 'Measure Shimmer PCA',
    # 'Measure Vocal Tract Estimates',

    'Visualize Pitch',
    'Visualize Intensity',
    'Visualize Formants'

]


# these are the types of values that are allowed to display, this is to prevent things like
# sound objects printed to screen. Adding a new type here will let it show up in the results
display_whitelist = [
    int,
    float,
    str
]