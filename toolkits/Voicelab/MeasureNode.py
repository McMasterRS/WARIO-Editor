## TODO: Not intended to be the final node, only while we are breaking out functionality
from pipeline.Node import Node
import numpy as np
import pandas as pd
from parselmouth import praat

class MeasureNode(Node):
    def process(self):
        pass

class MeasureVoiceFormantNode(Node):
    def process(self):
        voice = self.args["voice"]
        pitch = praat.call(voice, "To Pitch", 0.0, 50, 500)
        mean_f0 = praat.call(pitch, "Get mean", 0, 0, "Hertz")
        if 170 <= mean_f0 <= 300:
            max_formant = 5500
        elif mean_f0 < 170:
            max_formant = 5000
        else:
            max_formant = 8000


class MeasureVoiceDurationNode(Node):
    def process(self):
        pass

class MeasureVoicePitchNode(Node):
    def process(self):
        voice = self.args['voice']
        time_step = self.args['time step']
        pitch_floor = self.args['pitch floor']
        pitch_ceiling = self.args['pitch_ceiling']
        pitch = praat.call(voice, 'To Pitch', time_step, pitch_floor, pitch_ceiling)
        return {
            "pitch": pitch
        }

class MeasureVoiceHNRNode(Node):
    def process(self):
        voice = self.args['voice']
        min_pitch = self.args['min pitch']
        silence_threshold = self.args['silence threshold']
        periods_per_window = self.args['periods per window']
        hnr = praat.call(voice, "To Harmonicity", min_pitch, silence_threshold, periods_per_window)
        return {
            "hnr": hnr
        }

class VoiceToPointProcess(Node):
    def process(self):
        sound = self.args["sound"]
        floor = self.args["floor"]
        ceiling = self.args["ceiling"]
        measure_type = self.args["measure_type"]
        point_process = praat.call(sound, "To PointProcess (periodic, cc)", floor, ceiling)
        return {
            "point process": point_process
        }
        
class MeasureVoiceJitterNode(Node):
    def process(self):
        time_range = self.args['time_range']
        period_floors = self.args['period floors']
        period_ceilings = self.args['period ceilings']
        max_period_factor = self.args['max period factor']

        if measure_type = "local":
            jitter = call(point_process, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)
        elif measure_type = "local absolute":
            jitter = call(point_process, "Get jitter (local, absolute)", 0, 0, 0.0001, 0.02, 1.3)
        elif measure_type = "rap":
            jitter = call(point_process, "Get jitter (rap)", 0, 0, 0.0001, 0.02, 1.3)
        elif measure_type = "ppq5":
            jitter = call(point_process, "Get jitter (ppq5)", 0, 0, 0.0001, 0.02, 1.3)
        elif measure_type = "ddp":
            jitter = call(point_process, "Get jitter (ddp)", 0, 0, 0.0001, 0.02, 1.3)
        else
            jitter = None
        return {
            "jitter": jitter
        }


class MeasureVoiceShimmerNode(Node):
    def process(self):
        pass


class MeasureVoiceGender(Node):
    def process(self):
        pass

class PCAVoiceShimmerNode(Node):
    def process(self):
        pass

class PCAVoiceJitterNode(Node):
    def process(self):
        pass

class PCAVoiceFormantNode(Node):
    def process(self):
        pass
