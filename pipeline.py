from pipeline.NodeFactory import NodeFactory
from pipeline.NodzInterface import NodzInterface
from pipeline.Pipeline import Pipeline
from pipeline.Node import Node
from toolkits.Voicelab.MeasureNode import *
from toolkits.Voicelab.ManipulateNode import *

load_voice = LoadVoiceNode('load_voice')

measure_duration = MeasureVoiceDuration('measure_duration')
measure_pitch = MeasureVoicePitch('measure_pitch')
measure_hnr = MeasureHNR('measure_hnr')
measure_jitter = MeasureJitter('meaure_jitter')
measure_shimmer = MeasureShimmer('measure_shimmer')
measure_formants = MeasureVoiceFormant('measure_formant')
measure_vocal_tract = MeasureVocalTractEstimates('measure_vocal_tract')
measure_jitter_pca = MeasureJitterPCA('measure_jitter_pca')
measure_shimmer_pca = MeasureShimmerPCA('measure_shimmer_pca')
measure_formant_pca = MeasureFormantPCA('measure_formant_pca')

pipeline = Pipeline()

load_voice.args['voice_file'] = './test_voices/f4047_ah.wav'

pipeline.add(load_voice)
pipeline.add(measure_pitch)
pipeline.add(measure_duration)
pipeline.add(measure_hnr)
pipeline.add(measure_jitter)
pipeline.add(measure_shimmer)
pipeline.add(measure_formants)
pipeline.add(measure_vocal_tract)
pipeline.add(measure_jitter_pca)
pipeline.add(measure_shimmer_pca)
pipeline.add(measure_formant_pca)

pipeline.connect((load_voice, "voice"), (measure_pitch, "voice"))
pipeline.connect((load_voice, "voice"), (measure_duration, "voice"))
pipeline.connect((load_voice, "voice"), (measure_hnr, "voice"))
pipeline.connect((load_voice, "voice"), (measure_jitter, "voice"))
pipeline.connect((load_voice, "voice"), (measure_shimmer, "voice"))
pipeline.connect((load_voice, "voice"), (measure_formants, "voice"))

pipeline.connect((measure_formants, "formant_means"), (measure_vocal_tract, "formants"))

pipeline.connect((measure_jitter, "local_jitter"), (measure_jitter_pca, "local_jitter"))
pipeline.connect((measure_jitter, "localabsolute_jitter"), (measure_jitter_pca, "localabsolute_jitter"))
pipeline.connect((measure_jitter, "rap_jitter"), (measure_jitter_pca, "rap_jitter"))
pipeline.connect((measure_jitter, "ppq5_jitter"), (measure_jitter_pca, "ppq5_jitter"))
pipeline.connect((measure_jitter, "ddp_jitter"), (measure_jitter_pca, "ddp_jitter"))

pipeline.connect((measure_shimmer, "local_shimmer"), (measure_shimmer_pca, "local_shimmer"))
pipeline.connect((measure_shimmer, "localdb_shimmer"), (measure_shimmer_pca, "localdb_shimmer"))
pipeline.connect((measure_shimmer, "apq3_shimmer"), (measure_shimmer_pca, "apq3_shimmer"))
pipeline.connect((measure_shimmer, "aqpq5_shimmer"), (measure_shimmer_pca, "aqpq5_shimmer"))
pipeline.connect((measure_shimmer, "apq11_shimmer"), (measure_shimmer_pca, "apq11_shimmer"))
pipeline.connect((measure_shimmer, "dda_shimmer"), (measure_shimmer_pca, "dda_shimmer"))

pipeline.connect((measure_formants, "formant_means"), (measure_formant_pca, "formant_means"))

results = pipeline.start()
print(results)













# import parselmouth
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns

# class RootNode(Node):
#     def process(self):
#         print("Root")
#         return {
#             "OUT": 0
#         }

# class MiddleNode(Node):
#     def process(self):
#         print("Middle", self.args['IN'])
#         return {
#             "OUT": self.args['IN'] + 1
#         }

# class LeafNode(Node):
#     def process(self):
#         print("Leaf", self.args['IN'])

# root = RootNode(0)
# middle = MiddleNode(1)
# middle2 = MiddleNode(2)
# leaf = LeafNode(3)
# leaf2 = LeafNode(4)

# pipeline = Pipeline()
# measure_voice_all_node = MeasureVoiceAllNode('measure_voice_all_node')
# pipeline.add(measure_voice_all_node)

# # pipeline.connect((root, 'OUT'), (middle, 'IN'))
# # pipeline.connect((root, 'OUT'), (middle2, 'IN'))

# # pipeline.connect((middle, 'OUT'), (leaf, 'IN'))
# # pipeline.connect((middle, 'OUT'), (leaf2, 'IN'))

# results, done = pipeline.run_node(root)
# print(results)




# # sns.set() # Use seaborn's default style to make attractive graphs

# # # Plot nice figures using Python's "standard" matplotlib library
# # snd = parselmouth.Sound("test_voices/f4047_ah.wav")
# # snd = parselmouth.Sound("test_voices/f4047_ee.wav")
# # snd = parselmouth.Sound("test_voices/f4047_eh.wav")
# # # snd = parselmouth.Sound("test_voices/f4047_oh.wav")
# # # snd = parselmouth.Sound("test_voices/f4047_oo.wav")
# # plt.figure()
# # plt.plot(snd.xs(), snd.values.T)
# # plt.xlim([snd.xmin, snd.xmax])
# # plt.xlabel("time [s]")
# # plt.ylabel("amplitude")
# # plt.show() # or plt.savefig("sound.png"), or plt.savefig("sound.pdf")

# # def draw_spectrogram(spectrogram, dynamic_range=70):
# #     X, Y = spectrogram.x_grid(), spectrogram.y_grid()
# #     sg_db = 10 * np.log10(spectrogram.values)
# #     plt.pcolormesh(X, Y, sg_db, vmin=sg_db.max() - dynamic_range, cmap='afmhot')
# #     plt.ylim([spectrogram.ymin, spectrogram.ymax])
# #     plt.xlabel("time [s]")
# #     plt.ylabel("frequency [Hz]")

# # def draw_intensity(intensity):
# #     plt.plot(intensity.xs(), intensity.values.T, linewidth=3, color='w')
# #     plt.plot(intensity.xs(), intensity.values.T, linewidth=1)
# #     plt.grid(False)
# #     plt.ylim(0)
# #     plt.ylabel("intensity [dB]")

# # intensity = snd.to_intensity()
# # spectrogram = snd.to_spectrogram()
# # plt.figure()
# # draw_spectrogram(spectrogram)
# # plt.twinx()
# # draw_intensity(intensity)
# # plt.xlim([snd.xmin, snd.xmax])
# # plt.show() # or plt.savefig("spectrogram.pdf")



# # nodes, connections, global_vars = NodzInterface.load("./pipeline/saves/sample.json")
# # pipeline = Pipeline()

# # for node_id, node in nodes:
# #     pipeline.add(node)

# # print("connections")
# # for connection in connections:
# #     parent, child = connection
# #     pipeline.connect(parent, child)
# #     # print("connect", parent, child)
# #     # pipeline.connect(parent, child)

# # pipeline = Pipeline()

# # NodeFactory.import_node('CSVInputGUINode', 'default', 'CSVInputGUINode')
# # input_gui_node = NodeFactory.create_node("INPUT GUI", 'CSVInputGUINode')

# # NodeFactory.import_node('BasicMatplotOutputNode', 'default', 'BasicMatplotOutputNode')
# # plot_node = NodeFactory.create_node("PLOT GUI", 'BasicMatplotOutputNode')

# # pipeline.add(input_gui_node)
# # pipeline.add(plot_node)

# # pipeline.connect(parent=(input_gui_node, 'OUT'), child=(plot_node, 'X'))
# # pipeline.connect(parent=(input_gui_node, 'OUT'), child=(plot_node, 'Y'))

# # pipeline.start()