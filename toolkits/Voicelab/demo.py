import parselmouth
from parselmouth.praat import call
from sklearn.decomposition import PCA
from pipeline.Node import Node

def pitch_bounds(sound):
    "measures the ceiling and floor for a given voice"

    # measure pitch ceiling and floor
    broad_pitch = call(sound, "To Pitch (cc)", 0, 50, 15, "yes", 0.03, 0.45, 0.01, 0.35, 0.14, 800)
    broad_mean_f0: float = call(broad_pitch, "Get mean", 0, 0, "hertz")  # get mean pitch

    if broad_mean_f0 < 400:
        pitch2 = call(sound, "To Pitch (cc)", 0, 50, 15, "yes", 0.03, 0.45, 0.01, 0.35, 0.14, 500)
        pitch2_min_f0: float = call(pitch2, "Get minimum", 0, 0, "hertz", "Parabolic")  # get min pitch
        pitch2_max_f0: float = call(pitch2, "Get maximum", 0, 0, "hertz", "Parabolic")  # get max pitch
    else:
        pitch2 = call(sound, "To Pitch (cc)", 0, 50, 15, "yes", 0.03, 0.45, 0.01, 0.35, 0.14, 800)
        pitch2_min_f0: float = call(pitch2, "Get minimum", 0, 0, "hertz", "Parabolic")  # get min pitch
        pitch2_max_f0: float = call(pitch2, "Get maximum", 0, 0, "hertz", "Parabolic")  # get max pitch

    pitch_floor: float = pitch2_min_f0 * 0.9
    pitch_ceiling: float = pitch2_max_f0 * 1.1

    return pitch_floor, pitch_ceiling

class LoadVoiceNode(Node):
    def process(self):
        voice_file = self.args['voice_file']
        voice = parselmouth.Sound(voice_file)
        return {'voice': voice}

load_voice = LoadVoiceNode()
load_voice.args['voice_file'] = './test_voices/f4047_ah.wav'
res = load_voice.process()
voice = res['voice']
print(res)


class LoadVoicesNode(Node):
    def process(self):
        voices = {}
        for voice_file in self.args['voice_files']:
            voices[voice_file] = parselmouth.Sound(voice_file)
        return {'voices': voices}

class MeasureVoiceDuration(Node):
    def process(self):
        sound = self.args['voice']
        duration = call(sound, "Get total duration") 
        return { 'duration': duration}

class MeasureVoicePitch(Node):

    pitch_settings = {
        'pitch_method': 'To Pitch (ac)',
        'time_step': 0,
        'max_number_of_candidates': 15,
        'very_accurate': 'no',
        'silence_threshold': 0.03,
        'voicing_threshold': 0.45,
        'octave_cost': 0.01,
        'octave_jump_cost': 0.35,
        'voiced_unvoiced_cost': 0.14}

    def process(self):
        'measure pitch for incoming sound'

        sound = self.args['voice']
        # unit = self.args['unit']
        unit = "Hertz"
        file_duration: float = call(sound, "Get total duration")

        # use auto-correlation for longer sounds & cross-correlation for shorter sounds
        if file_duration < 0.25:
            # cross correlation
            pitch_method = "To Pitch (cc)"
        else:
            # auto correlation
            pitch_method = "To Pitch (ac)"

        pitch_floor, pitch_ceiling = pitch_bounds(sound)

        pitch = call(sound,
            pitch_method,
            self.pitch_settings["time_step"], 
            pitch_floor,
            self.pitch_settings["max_number_of_candidates"],
            self.pitch_settings["very_accurate"],
            self.pitch_settings["silence_threshold"],
            self.pitch_settings["voicing_threshold"],
            self.pitch_settings["octave_cost"],
            self.pitch_settings["octave_jump_cost"],
            self.pitch_settings["voiced_unvoiced_cost"],
            pitch_ceiling)

        mean_f0: float = call(pitch, "Get mean", 0, 0, unit)
        stdev_f0: float = call(pitch, "Get standard deviation", 0, 0, unit)  # get standard deviation
        min_f0: float = call(pitch, "Get minimum", 0, 0, "hertz", "Parabolic")
        max_f0: float = call(pitch, "Get maximum", 0, 0, "hertz", "Parabolic")

        return {
            'mean_f0': mean_f0,
            'stdev_f0': stdev_f0,
            'min_f0': min_f0,
            'max_f0': max_f0,
            'pitch_settings': self.pitch_settings
        }

class MeasureHNR(Node):

    hnr_settings = {
        'hnr_floor': 50,
        'hnr_ceiling': 500,
        'hnr_algorithm': 'To Harmonicity (cc)',
        'hnr_timestep': 0.01,
        'hnr_silence_threshold': 0.1,
        'hnr_periods_per_window': 1.0
    }

    def process(self):
        'hnr'

        sound = self.args['sound']

        # measure pitch ceiling and floor
        broad_pitch = call(sound, "To Pitch (cc)", 0, 50, 15, "yes", 0.03, 0.45, 0.01, 0.35, 0.14, 800)
        broad_mean_f0: float = call(broad_pitch, "Get mean", 0, 0, "hertz")  # get mean pitch

        if broad_mean_f0 < 400:
            pitch2 = call(sound, "To Pitch (cc)", 0, 50, 15, "yes", 0.03, 0.45, 0.01, 0.35, 0.14, 500)
            pitch2_min_f0: float = call(pitch2, "Get minimum", 0, 0, "hertz", "Parabolic")  # get min pitch
            pitch2_max_f0: float = call(pitch2, "Get maximum", 0, 0, "hertz", "Parabolic")  # get max pitch
        else:
            pitch2 = call(sound, "To Pitch (cc)", 0, 50, 15, "yes", 0.03, 0.45, 0.01, 0.35, 0.14, 800)
            pitch2_min_f0: float = call(pitch2, "Get minimum", 0, 0, "hertz", "Parabolic")  # get min pitch
            pitch2_max_f0: float = call(pitch2, "Get maximum", 0, 0, "hertz", "Parabolic")  # get max pitch

        pitch_floor: float = pitch2_min_f0 * 0.9
        pitch_ceiling: float = pitch2_max_f0 * 1.1

        harmonicity: float = call(sound,
            self.hnr_settings["hnr_algorithm"],
            self.hnr_settings['hnr_timestep'],
            pitch_floor,
            self.hnr_settings['hnr_silence_threshold'],
            self.hnr_settings['hnr_periods_per_window'])

        hnr: float = call(harmonicity, "Get mean", 0, 0)

        return {
            "hnr": hnr,
            "hnr_settings": hnr_settings
        }


class MeasureJitter(Node):

    jitter_settings = {
        'floor': 50,
        'ceiling': 500,
        'start_time': 0,
        'end_time': 0,
        'shortest_period': 0.0001,
        'longest_period': 0.02,
        'maximum_period_factor': 1.3
    }

    def process(self):

        'measure jitter'

        sound = self.args['sound']
        pitch_floor, pitch_ceiling = pitch_bounds(sound)

        point_process: object = call(sound, "To PointProcess (periodic, cc)",
            pitch_floor,
            pitch_ceiling)

        local_jitter: float = call(point_process, "Get jitter (local)",
            self.jitter_settings['start_time'],
            self.jitter_settings['end_time'],
            self.jitter_settings['shortest_period'],
            self.jitter_settings['longest_period'],
            self.jitter_settings['maximum_period_factor'])

        # todo change this so that it accepts defaults unless user is in advanced mode
        localabsolute_jitter: float = call(point_process, "Get jitter (local, absolute)",
            self.jitter_settings['start_time'],
            self.jitter_settings['end_time'],
            self.jitter_settings['shortest_period'],
            self.jitter_settings['longest_period'],
            self.jitter_settings['maximum_period_factor'])

        rap_jitter: float = call(point_process, "Get jitter (rap)",
            self.jitter_settings['start_time'],
            self.jitter_settings['end_time'],
            self.jitter_settings['shortest_period'],
            self.jitter_settings['longest_period'],
            self.jitter_settings['maximum_period_factor'])

        ppq5_jitter: float = call(point_process, "Get jitter (ppq5)",
            self.jitter_settings['start_time'],
            self.jitter_settings['end_time'],
            self.jitter_settings['shortest_period'],
            self.jitter_settings['longest_period'],
            self.jitter_settings['maximum_period_factor'])

        ddp_jitter: float = call(point_process, "Get jitter (ddp)",
            self.jitter_settings['start_time'],
            self.jitter_settings['end_time'],
            self.jitter_settings['shortest_period'],
            self.jitter_settings['longest_period'],
            self.jitter_settings['maximum_period_factor'])

        return {
            'local_jitter': local_jitter,
            'localabsolute_jitter': localabsolute_jitter,
            'rap_jitter': rap_jitter,
            'ppq5_jitter': ppq5_jitter,
            'ddp_jitter': ddp_jitter,
            'jitter_settings': jitter_settings
        }

class MeasureShimmer(Node):
        
    shimmer_settings = {
        'floor': 50,
        'ceiling': 500,
        'start_time': 0,
        'end_time': 0,
        'shortest_period': 0.0001,
        'longest_period': 0.02,
        'maximum_period_factor': 1.3,
        'maximum_amplitude': 1.6
    }

    def process(self):
        'shimmer'

        floor, ceiling = pitch_bounds(sound)

        point_process: object = call(sound, "To PointProcess (periodic, cc)",
            self.shimmer_settings['floor'],
            self.shimmer_settings['ceiling'])

        local_shimmer: float = call([sound, point_process], "Get shimmer (local)",
            self.shimmer_settings['start_time'],
            self.shimmer_settings['end_time'],
            self.shimmer_settings['shortest_period'],
            self.shimmer_settings['longest_period'],
            self.shimmer_settings['maximum_period_factor'],
            self.shimmer_settings['maximum_amplitude'])

        localdb_shimmer: float = call([sound, point_process], "Get shimmer (local_dB)",
            self.shimmer_settings['start_time'],
            self.shimmer_settings['end_time'],
            self.shimmer_settings['shortest_period'],
            self.shimmer_settings['longest_period'],
            self.shimmer_settings['maximum_period_factor'],
            self.shimmer_settings['maximum_amplitude'])

        apq3_shimmer: float = call([sound, point_process], "Get shimmer (apq3)",
            self.shimmer_settings['start_time'],
            self.shimmer_settings['end_time'],
            self.shimmer_settings['shortest_period'],
            self.shimmer_settings['longest_period'],
            self.shimmer_settings['maximum_period_factor'],
            self.shimmer_settings['maximum_amplitude'])

        aqpq5_shimmer: float = call([sound, point_process], "Get shimmer (apq5)",
            self.shimmer_settings['start_time'],
            self.shimmer_settings['end_time'],
            self.shimmer_settings['shortest_period'],
            self.shimmer_settings['longest_period'],
            self.shimmer_settings['maximum_period_factor'],
            self.shimmer_settings['maximum_amplitude'])

        apq11_shimmer: float = call([sound, point_process], "Get shimmer (apq11)",
            self.shimmer_settings['start_time'],
            self.shimmer_settings['end_time'],
            self.shimmer_settings['shortest_period'],
            self.shimmer_settings['longest_period'],
            self.shimmer_settings['maximum_period_factor'],
            self.shimmer_settings['maximum_amplitude'])

        dda_shimmer: float = call([sound, point_process], "Get shimmer (dda)",
            self.shimmer_settings['start_time'],
            self.shimmer_settings['end_time'],
            self.shimmer_settings['shortest_period'],
            self.shimmer_settings['longest_period'],
            self.shimmer_settings['maximum_period_factor'],
            self.shimmer_settings['maximum_amplitude'])

        return {
            'local_shimmer': local_shimmer,
            'localdb_shimmer': localdb_shimmer,
            'apq3_shimmer': apq3_shimmer,
            'aqpq5_shimmer': aqpq5_shimmer,
            'apq11_shimmer': apq11_shimmer,
            'dda_shimmer': dda_shimmer,
            'shimmer_settings': shimmer_settings
        }

class MeasureVoiceFormant(Node):

    formant_settings = {
        'time_step': 0, # a zero value is equal to 25% of the window length
        'max_number_of_formants': 5,  # always one more than you are looking for
        'maximum_formant': 5500,
        'window_length(s)': 0.025,
        'pre_emphasis_from': 50,
        'pitch_floor': 50,
        'pitch_ceiling': 500
    }

    def process(self):
        'formants'

        sound = self.args['sound']

        if method == "formants_praat_manual":
            self.formant_settings['max_formant'] = automatic_parameters.formants_praat_manual(sound)

        elif method == "sweep":
            self.formant_settings['max_formant'] = automatic_parameters.calculate_best_ceiling()
            # todo warn user this takes a long time
            # todo find a way for user to get from user the speaker identity and vowels from file names so we can process
            #  this

        formant_object = call(sound, "To Formant (burg)",
            self.formant_settings['time_step'],
            self.formant_settings['max_number_of_formants'],
            self.formant_settings['max_formant'],
            self.formant_settings['window_length(s)'],
            self.formant_settings['pre_emphasis_from']
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
            'f1': {
                'mean': f1_mean,
                'median': f1_median
            },
            'f2': {
                'mean': f2_mean,
                'median': f2_median
            },
            'f3': {
                'mean': f3_mean,
                'median': f3_median
            },
            'f4': {
                'mean': f4_mean,
                'median': f4_median
            },
            'formant_settings':formant_settings
        }

class MeasureVocalTractEstimates(Node):
    def process(self):
        'vocal_tract_estimates_mean'

        f1 = self.args['f1']
        f2 = self.args['f2']
        f3 = self.args['f3']
        f4 = self.args['f4']

        formant_dispersion = (f4 - f1) / 3
        average_formant = (f1 + f2 + f3 + f4) / 4
        geometric_mean = (f1 * f2 * f3 * f4) ** 0.25

        fitch_vtl = (
            (1 *(35000 / (4 * f1))) +
            (3 * (35000 / (4 * f2))) +
            (5 * (35000 / (4 * f3))) +
            (7 * (35000 / (4 * f4)))) / 4

        # Reby Method
        xysum = (0.5 * f1) + (1.5 * f2) + (2.5 * f3) + (3.5 * f4)
        xsquaredsum = (0.5 ** 2) + (1.5 ** 2) + (2.5 ** 2) + (3.5 ** 2)
        delta_f = xysum / xsquaredsum
        vtl_delta_f = 35000 / (2 * delta_f)

        return {
            'formant_dispersion': formant_dispersion,
            'average_formant': average_formant,
            'geometric_mean': geometric_mean,
            'fitch_vtl': fitch_vtl,
            'delta_f': delta_f,
            'vtl_delta_f': vtl_delta_f
        }

class MeasureJitterPCA(Node):
    def process(self):

        df = self.args['df']
        try:
            # z-score the Jitter measurements
            measures = ['localJitter', 'localabsoluteJitter', 'rapJitter', 'ppq5Jitter', 'ddpJitter']
            x = df.loc[:, measures].values
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

class MeasureShimmerPca(Node):
    
    def process(self):

        df = self.args['df']

        try:
            # z-score the Shimmer measurements
            measures = ['localShimmer', 'localdbShimmer', 'apq3Shimmer', 'apq5Shimmer', 'apq11Shimmer', 'ddaShimmer']
            x = df.loc[:, measures].values
            x = StandardScaler().fit_transform(x)
            # Run the PCA
            pca = PCA(n_components=1)
            principal_components = pca.fit_transform(x)
            shimmer_pca_df = pd.DataFrame(data=principal_components, columns=['ShimmerPCA'])
            return shimmer_pca_df
        except:
            print('Shimmer PCA failed.  Please check your data') # todo make this an error message

class MeasureFormantPCA(Node):

    # Takes a dataframe with f1-4
    def process(self):
        ""

        df = self.args['df']
        measures = self.args['measures']

        # PCA of the formants
        x = df.loc[:, measures].values
        x = StandardScaler().fit_transform(x)
        
        # Run the PCA
        pca = PCA(n_components=1)
        principal_components = pca.fit_transform(x)

        return {
            'principal_components': principal_components
        }