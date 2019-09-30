## TODO: Not intended to be the final node, only while we are breaking out functionality
import parselmouth
from pipeline.Node import Node
from parselmouth.praat import call

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

class ManipulatePitchNode(Node):

    def process(self):
        
        sound = self.args['voice']
        unit = self.args['unit']
        factor = self.args['factor']
        # sound_name = self.args['sound_name']

        f0min, f0max = pitch_bounds(sound)

        manipulation = call(sound, "To Manipulation", 0.001, f0min, f0max)
        pitch_tier = call(manipulation, "Extract pitch tier")
        call(pitch_tier, "Shift frequencies", f0min, f0max, factor, unit)
        call([pitch_tier, manipulation], "Replace pitch tier")
        manipulated_sound = call(manipulation, "Get resynthesis (overlap-add)")
        manipulated_sound.scale_intensity(70)
        # manipulated_pitch_name = sound_name + "_pitch_manipulated_{}_{}.wav".format(factor, unit)
        # manipulated_sound.save(manipulated_pitch_name, "WAV")

        return {
            'manipulated_sound': manipulated_sound
        }

class ManipulateFormantsNode(Node):

    def process(self):
        sound = self.args['voice']
        unit = self.args['unit']
        factor = self.args['factor']
        # sound_name = self.args['sound_name']

        factor_percent = round(factor*100)
        f0min, f0max = pitch_bounds(sound)
        
        manipulated_sound = call(sound, "Change gender", f0min, f0max, factor, 0, 1, 1)
        manipulated_sound.scale_intensity(70)

        return {
            'manipulated_sound': manipulated_sound
        }

class ManipulatePitchAndFormants(Node):

    def process(self):

        sound = self.args['voice']
        unit = self.args['unit']
        formant_factor = self.args['formant_factor']
        pitch_factor = self.args['pitch_factor']
        # sound_name = self.args['sound_name']
        duration = self.args['duration']

        f0min, f0max = pitch_bounds(sound)

        pitch_expression = "self" + str(pitch_factor)

        # formant factor is in format e.g. down 5%
        vtl_factor = 1 - formant_factor # This makes vocal tract 5% longer by making formants shift down 5%
        vtl_factor_percent = round(vtl_factor*100)
        sampling_rate = call(sound, "Get sample rate")

        # create Pitch & Manipulation objects
        pitch = call(sound, "To Pitch", 0.001, f0min, f0max)

        # pitch = sound.to_pitch(0.001, f0min, f0max)
        manipulation = call([pitch, sound], "To Manipulation")

        # apply the appropriate transformation to the Pitch object
        # includes vtfactor because of subsequent rescaling
        pitch_formula = pitch_expression + '*' + str(vtl_factor)
        pitch = call(pitch, "Formula", pitch_formula)

        # turn it into a PitchTier and place it into the Analysis object
        pitch_tier = call([manipulation, pitch], "Down to pitch tier")
        manipulation = call([pitch_tier, manipulation], "Replace pitch tier")

        # change to new duration
        DurationTier = call(sound, "Create DurationTier", "DurationTier", 0, duration)
        DurationTier.add_point(0, 1/vtl_factor)
        manipulation = call([DurationTier, manipulation], "Replace duration tier")
        manipulated_sound = call(manipulation, "Get resynthesis (overlap-add)")
        manipulated_sound.override_sampling_frequency(sampling_rate)
        manipulated_sound.scale_intensity(70)

        # manipulated_pitch_and_formant_name = sound_name + \
        #     f"_formant_manipulated_pitch_{pitch_factor}" \
        #     f"_formants_{vtl_factor_percent}.wav"
        # manipulated_sound.save(manipulated_pitch_and_formant_name, "WAV")
        
        return {
            'manipulated_sound': manipulated_sound
        }

class ManipulateGenderAge(Node):

    def process(self):

        sound = self.args['voice']
        call(sound, "Scale intensity", 70)
        pitch = call(sound, "To Pitch", 0.0, 60, 500)
        meanF0 = call(pitch, "Get mean", 0, 0, "Hertz")

        if meanF0 > 159:
            gender = "female"
        else:
            gender = "male"

        if gender == "female":
            male = call(sound, "Change gender", 60, 500, 0.8, 100, 1, 1)
            female = call(sound, "Change gender", 60, 500, 1, 220, 1, 1)
            child = call(sound, "Change gender", 60, 500, 1.5, 350, 1, 1)
        elif gender == "male":
            male = call(sound, "Change gender", 60, 500, 1, 100, 1, 1)
            female = call(sound, "Change gender", 60, 500, 1.2, 220, 1, 1)
            child = call(sound, "Change gender", 60, 500, 1.6, 350, 1, 1)

        return {
            'male_voice': male,
            'female_voice': female,
            'child_voice': child
        }