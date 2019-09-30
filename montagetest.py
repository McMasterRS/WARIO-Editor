import mne

from mne.datasets import sample
from mne.datasets import fetch_fsaverage  
    
data_path = sample.data_path()
raw_fname = data_path + '/MEG/sample/sample_audvis_filt-0-40_raw.fif'
event_fname = data_path + '/MEG/sample/sample_audvis_filt-0-40_raw-eve.fif'

raw = mne.io.read_raw_fif(raw_fname, preload=True)

raw.pick_types(meg=False, eeg=True, eog=True)   
print(raw.info)
#   raw.set_montage(mne.channels.read_montage('standard_1020'))
fig = raw.plot_sensors()

fig.show()