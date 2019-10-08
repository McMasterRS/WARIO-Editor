from toolkits.Voicelab.VoicelabNode import VoicelabNode

class MeasureIntensityNode(VoicelabNode):

    ###############################################################################################
    # process: WARIO hook called once for each voice file.
    ###############################################################################################

    def process(self):
        voice = self.args['voice']
        intensity = voice.to_intensity()
        return {
            'Voice Intensity': intensity
        }
