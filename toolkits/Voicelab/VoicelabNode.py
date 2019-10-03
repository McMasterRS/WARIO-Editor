from pipeline.Node import Node
from parselmouth.praat import call

###################################################################################################
###################################################################################################

class VoicelabNode(Node):
    
    def pitch_bounds(self, sound):
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

    def pitch_floor(self, sound):
        return self.pitch_bounds(sound)[0]

    def pitch_ceiling(self, sound):
        return self.pitch_bounds(sound)[1]