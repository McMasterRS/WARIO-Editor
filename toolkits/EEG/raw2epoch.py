from pipeline.Node import Node
import mne

class raw2epoch(Node):

    def __init__(self, name, params):
        super(raw2epoch, self).__init__(name, params)
        
        
    def process(self):
        '''
        Takes an MNE Raw object and trigger data and creates anan Epochs object 
        and Evoked object.
        '''
        Raw = self.args["Raw"]
        sfreq = Raw.info['sfreq']
        
        # NEED TO IMPORT T AND Y
     
        ###################
    #    Y[Y==3] = 1
        ##################
        
        # MNE needs trigger data in a certain format
        trigger_data = np.concatenate((np.expand_dims(T*sfreq,axis=1),
                                       np.zeros((T.shape[0],1)),
                                       np.expand_dims(Y,axis=1)),axis=1).astype(int)
        
        # create Epochs object
        Epochs = mne.Epochs(Raw, events=trigger_data, event_id = dict(NMW=1,MW=2),
                            tmin=-epochLength, tmax=0.0, proj=False, picks=None, baseline=(None,None),
                            reject=None, flat=None, preload=True, reject_by_annotation=True,
                            detrend=1, verbose=20)
        
        # create Evoked object
        Evoked = [Epochs[name].average() for name in ('NMW', 'MW')]
      
        return {"Epoch Data" : Epochs, "Evoked Data" : Evoked, "Trigger Data" :trigger_data}
