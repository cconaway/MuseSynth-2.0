import collections
import numpy as np
import math
import time

from eeg_fft import EEG_fft
    

class ClientUtility(object):

    def __init__(self, msg_prefix):
        self.msg_prefix = msg_prefix

    def send_to_clients(self, clients, send_address, output):
        for client in clients:
            #print('{}_{}_{}'.format(client, send_address, i), output)
            if self.msg_prefix == None: 
                client.send_message('{}'.format(send_address), output)
            else:
                client.send_message('{}{}'.format(self.msg_prefix, send_address), output)
            time.sleep(1)
            
class RangeLimiter(object):

    def __init__(self, input_range, output_range):
        self.outmax = output_range[1]
        self.outmin = output_range[0]
        self.inmax = input_range[1]
        self.inmin = input_range[0]

        self.input_range = (self.inmax - self.inmin)
        self.output_range = (self.outmax - self.outmin)

    def squeeze(self, data):
        output = [(((d-self.inmin) * self.output_range) / self.input_range) + self.outmin for d in data]
        return output



class MotionHandler(object):

    def __init__(self, input_range, output_range, msg_prefix=None, window=30, data_streams=3, send_address='/acc_xyz'):
        self.client_utility = ClientUtility(msg_prefix)
        self.rangelimiter = RangeLimiter(input_range, output_range)

        self.send_address = send_address
        self.window = window
        self.directions = np.arange(data_streams)
        self.output = list(np.arange(data_streams))

        self.ques = []
        for i in range(data_streams):
            self.ques.append(collections.deque())

    def run(self, address: str, fixed_args, *args):
        
        args = self.rangelimiter.squeeze(args)
        for d, que in zip(self.directions, self.ques):
            if len(self.ques[0]) == self.window:
                que.popleft()
                que.append(args[d])

            else:
                que.append(args[d])
            self.output[d]= sum(que)/len(que)

        self.client_utility.send_to_clients(fixed_args[0], self.send_address, self.output)


class RawEEGHandler(object):

    def __init__(self, process_fft=False, msg_prefix=None):
        self.send_address = '/raw_eeg'
        self.client_utility = ClientUtility(msg_prefix)
        self.procfft = process_fft

        if self.procfft == True:
            self.eeg_fft = EEG_fft()

    def run(self, address: str, fixed_args, *args):
        self.client_utility.send_to_clients(fixed_args[0], self.send_address, args)

        if self.procfft == True:
            output = self.eeg_fft.run_fft(args)

            if output is None:
                pass
            else:
                print(output)


class WaveHandler(object):

    def __init__(self, input_range, output_range, window=30, msg_prefix=None):
        self.client_utility = ClientUtility(msg_prefix)
        self.rangelimiter = RangeLimiter(input_range, output_range)

        self.send_address = '/relative_wave'

        self.hsi = [-1,-1,-1,-1]
        self.waves = [0,1,2,3,4]
        self.absolute_wavepower = [-1,-1,-1,-1,-1]
        self.relative_wavepower = [-1,-1,-1,-1,-1]

        self.window = window
        self.ques = []
        for i in range(len(self.absolute_wavepower)):
            self.ques.append(collections.deque())

    def run_hsi(self, address: str, *args):
        self.hsi = args

    def run(self, address: str, fixed_args, *args):
        wave = fixed_args[1]
        output = [-1,-1,-1,-1,-1]


        data_from_signal = self._sum_ifsignal(args)
        if data_from_signal == 0.001:
            self.absolute_wavepower[wave] = 0.1
        else:
            self.absolute_wavepower[wave] = data_from_signal


        self.relative_wavepower[wave] = self._compute_relative(wave, self.absolute_wavepower)

        for w, que in zip(self.waves, self.ques):
            if len(self.ques[w]) == self.window:
                que.popleft()
                que.append(self.relative_wavepower[w])
            else:
                que.append(self.relative_wavepower[w])
            output[w] = sum(que)/len(que) 

        output = self.rangelimiter.squeeze(output)
        self.client_utility.send_to_clients(fixed_args[0], self.send_address, output)

    def _sum_ifsignal(self, args):
        sumVal = 0
        n = 0

        for i in range(4):
            if (self.hsi[i] == 1):
                sumVal += args[i]
                n += 1

        if n == 0:
            return 0.001
        else:
            return sumVal/n

    @staticmethod
    def _compute_relative(wave, absolute_wavepower):

        return (math.pow(10, absolute_wavepower[wave]) / 
            (math.pow(10, absolute_wavepower[0]) +
            math.pow(10, absolute_wavepower[1]) +
            math.pow(10, absolute_wavepower[2]) +
            math.pow(10, absolute_wavepower[3]) +
            math.pow(10, absolute_wavepower[4]))) 


class SplitWaveHandler(object):

    def __init__(self, input_range, output_range, wave_name='alpha', window=30, msg_prefix=None):
        self.client_utility = ClientUtility(msg_prefix)
        self.rangelimiter = RangeLimiter(input_range, output_range)

        self.send_address = '{}_Tp9_Af7_Af8_Tp10'.format(wave_name)

        self.wave_data = [-1,-1,-1,-1] #sensor data

        self.window = window
        self.ques = []
        for i in range(len(self.wave_data)):
            self.ques.append(collections.deque())

    def run(self, address: str, fixed_args, *args):
        output = [-1,-1,-1,-1]
        
        #args = self.rangelimiter.squeeze(args)
        #print(args) #check the magnitude of the split.
        for i, que in enumerate(self.ques):
            if len(que) == self.window:
                que.popleft()
                que.append(args[i])

            else:
                que.append(args[i])

            output[i]= sum(que)/len(que)

        self.client_utility.send_to_clients(fixed_args[0], self.send_address, output)

        



        

        
        

        