from toolkits.Voicelab.VoicelabNode import VoicelabNode

class MeasureIntensityNode(VoicelabNode):
    def process(self):
        voice = self.args['voice']
        intensity = voice.to_intensity()
        return {
            'intensity': intensity
        }
