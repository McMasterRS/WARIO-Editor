from parselmouth.praat import call
from VoicelabWizard.AutomaticParams import *

import toolkits.Voicelab as Voicelab

# List of all available operations the user can perform as well as their associated function node
avialable_functions = {

    'Measure Duration': Voicelab.MeasureDurationNode('Measure Duration'),
    'Measure Pitch': Voicelab.MeasurePitchNode('Measure Pitch'),
    'Measure Harmonicity': Voicelab.MeasureHarmonicityNode('Measure Harmonicity'),
    'Measure Jitter': Voicelab.MeasureJitterNode('Measure Jitter'),
    'Measure Shimmer': Voicelab.MeasureShimmerNode('Measure Shimmer'),
    'Measure Formants': Voicelab.MeasureFormantNode('Measure Formants'),
    'Measure Jitter PCA': Voicelab.MeasureJitterPCANode('Measure Jitter PCA'),
    'Measure Shimmer PCA': Voicelab.MeasureShimmerPCANode('Measure Shimmer PCA'),
    'Measure Formant PCA' : Voicelab.MeasureFormantPCANode('Measure Formant PCA'),
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
    str,
    list
]