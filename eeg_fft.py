import numpy as np
import scipy.signal
import collections

class EEG_fft(object):

    def __init__(self):
        self.fft_len = 2048
        self.sr = 256
        self.fr = self.sr/self.fft_len

        self.window = scipy.signal.windows.hamming(self.fft_len)
        self.t = np.arange(0, self.fft_len/self.sr, 1/self.sr)
        self.dt = self.t[1] - self.t[0]

        self.Nyq = 1/self.dt/2
        self.order = 100
        self.pad_len = (self.fft_len-self.order)
        self.filt_lp = scipy.signal.firwin(self.order, 14/self.Nyq)
        self.filt_hp = scipy.signal.firwin(self.order+1, 7/self.Nyq, pass_zero=False)
        self.notch_a, self.notch_b = scipy.signal.iirnotch(60/self.Nyq, self.order)
        
        self.sensor_data = collections.deque()

    def _hamm_spectrum(self, s, window, hamm=True):
        s = s - np.mean(s)
        sh = window * s if hamm else s

        sf = np.fft.rfft(sh)
        return np.abs(sf)

    def _series_filter(self, data):
        data_notch = scipy.signal.filtfilt(self.notch_a, self.notch_b, data)
        data_lp = scipy.signal.filtfilt(self.filt_lp, 1, data_notch, padlen=self.pad_len) 
        data_out = scipy.signal.filtfilt(self.filt_hp, 1, data_lp, padlen=self.pad_len)

        return data_out

    def _spectrogram(self, data):
        if len(data) != self.fft_len:
            return -1
        filt_data = self._series_filter(data)
        data_fft = self._hamm_spectrum(filt_data, self.window)
        

    def run_fft(self, *args):
        
        test = args[0]

        if len(self.sensor_data) == self.fft_len:
            self.sensor_data.popleft()
            self.sensor_data.append(test)
            
            out = self._spectrogram(self.sensor_data)
            

        else:
            self.sensor_data.append(test)

        print(out)
        return out


#Run some tests to see output. Then find a way to split the bands out.
        

