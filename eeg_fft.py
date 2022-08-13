import numpy as np
import scipy.signal
import collections
import time

class EEG_fft(object):

    def __init__(self):
        self.fft_len = 2048
        self.sr = 256
        self.fr = self.sr/self.fft_len

        self.window = scipy.signal.windows.hamming(self.fft_len)
        self.t = np.arange(0, self.fft_len/self.sr, 1/self.sr)
        self.dt = self.t[1] - self.t[0]

        self.Nyq = 1/self.dt/2
        self.order = 30 #Get coeffients
        self.pad_len = self.fft_len-self.order

        lowpass = 14
        highpass = 7
        notch = 60

        self.filt_lp = scipy.signal.firwin(numtaps=self.order, cutoff=lowpass, fs=self.sr)
        self.filt_hp = scipy.signal.firwin(numtaps=self.order+1, cutoff=highpass/self.Nyq, pass_zero=False)
        
        self.notch_a, self.notch_b = scipy.signal.iirnotch(notch, self.order, self.sr)
        
        self.sensor_data = collections.deque()
        self.state = True

    def _hamm_spectrum(self, s, window, hamm=True):
        s = s - np.mean(s)
        sh = window * s if hamm else s

        sf = np.fft.rfft(sh)
        return np.abs(sf)

    def _series_filter(self, data): #data = len2048
        
        
        data_notch = scipy.signal.filtfilt(self.notch_a, self.notch_b, data)
        data_lp = scipy.signal.filtfilt(self.filt_lp, 1, data_notch, padlen=self.pad_len) 
        data_out = scipy.signal.filtfilt(self.filt_hp, 1, data_lp, padlen=self.pad_len)
        
        return data_out

    def _spectrogram(self, data):
        if len(data) != self.fft_len:
            return -1

        filt_data = self._series_filter(data)
        data_fft = self._hamm_spectrum(filt_data, self.window)
        return data_fft

    def run_fft(self, args):

        test = args[0] #just doing one sensor
        if self.state == True:
            if len(self.sensor_data) == self.fft_len:
                self.sensor_data.popleft()
                self.sensor_data.append(test)
                self.state = False

                output = self._spectrogram(self.sensor_data)
                self.sensor_data.clear()
                self.state = True
                
                return output

            else:
                self.sensor_data.append(test)
        else:
            pass


        