from pipeline.Task import Task
import mne

class floatOut(Task):
    def run(self, data, badchans, lowPass, highPass):
        Raw = mne.io.RawArray(data,info,first_samp=0)
        Raw.set_montage(montage, set_dig=True)
        Raw.info['bads'] = badchans
        Pickchans = mne.pick_types(Raw.info,eeg=True)
        Raw.pick_types(eeg=True,exclude='bads')
        Raw.set_eeg_reference('average',projection=False)
        # Raw.set_eeg_reference(ref_channels=[],projection=False)
        Raw.filter(f1, f2, n_jobs=1, fir_design='firwin')
            
        return Raw, Pickchans