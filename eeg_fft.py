import numpy as np
import scipy.signal
import collections
import time

class EEG_fft(object):

    """Check the filters and figure out how to seperate the bands."""

    def __init__(self):
        self.fft_len = 256
        self.sr = 256
        self.fr = self.sr/self.fft_len

        self.window = scipy.signal.windows.hamming(self.fft_len)
        self.t = np.arange(0, self.fft_len/self.sr, 1/self.sr)
        self.dt = self.t[1] - self.t[0]

        self.Nyq = 1/self.dt/2
        self.order = 30 #Get coeffients
        self.pad_len = self.fft_len-self.order

        lowpass = 90
        highpass = 0.5
        notch = 60

        self.filt_lp = scipy.signal.firwin(numtaps=self.order, cutoff=lowpass, fs=self.sr)
        self.filt_hp = scipy.signal.firwin(numtaps=self.order+1, cutoff=highpass/self.Nyq, pass_zero=False)
        
        self.notch_a, self.notch_b = scipy.signal.iirnotch(notch, self.order, self.sr)
        
        self.sensor_data = collections.deque()
        self.state = True
        
        self.dataques = []
        for i in range(4):
            self.dataques.append(collections.deque())

    def _hamm_spectrum(self, s, window, hamm=False):
        s = s - np.mean(s)
        sh = window * s if hamm else s

        sf = np.fft.rfft(sh)
        #sf = scipy.signal.stft(sh, self.sr, nperseg=1024, window='hamm')
        
        return np.abs(sf) #squared gives PSD?V2 Hz−1

    def _series_filter(self, data): #data = len2048
        
        data_notch = scipy.signal.filtfilt(self.notch_a, self.notch_b, data)
        data_lp = scipy.signal.filtfilt(self.filt_lp, 1, data_notch, padlen=self.pad_len) 
        data_out = scipy.signal.filtfilt(self.filt_hp, 1, data_lp, padlen=self.pad_len)
        
        return data_out

    def _spectrogram(self, data):
        if len(data) != self.fft_len:
            return -1

        filt_data = self._series_filter(data)
        data_fft = self._hamm_spectrum(s=filt_data, window=self.window)

        return data_fft

    def run_fft(self, args):

        output= np.zeros((4,129))
        if self.state == True:
            if len(self.dataques[0]) == self.fft_len:
                self.state = False #Set the reciever to stop.
                
                s = [0,1,2,3]
                for s, dataque in zip(s, self.dataques):
                    output[s] = self._spectrogram(dataque)

                for dataque in self.dataques:
                    dataque.clear()
                self.state = True
            else:
                for d, dataque in zip(args, self.dataques):
                    dataque.append(d)
        else:
            pass
                    

        