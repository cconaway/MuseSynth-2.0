import collections
import numpy as np
import math
import time

def send_to_client(client, address, *args):
    client.send(address, args[0])
    time.sleep(1)

class MotionHandler(object):

    def __init__(self, window=30, data_streams=3, send_address='acc_xyz'):
        self.send_address = send_address
        self.window = window
        self.directions = np.arange(data_streams)
        self.output = list(np.arange(data_streams))

        self.ques = []
        for i in range(data_streams):
            self.ques.append(collections.deque())

    def run(self, address: str, client, *args):
        

        for d, que in zip(self.directions, self.ques):
            if len(self.ques[0]) == self.window:
                que.popleft()
                que.append(args[d])

            else:
                que.append(args[d])

            self.output[d]= sum(que)/len(que)

        client[0].send_message('{}'.format(self.send_address), self.output)
        time.sleep(1)

class RawEEGHandler(object):
    
    def __init__(self):
        self.send_address = 'raw_eeg'

    def run(self, address: str, client, *args):
        client[0].send_message('{}'.format(self.send_address), args)


class WaveHandler(object):

    def __init__(self, window=30):
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
        client = fixed_args[0]
        wave = fixed_args[1]
        output = [-1,-1,-1,-1,-1]
        # f f f f wave

        #print('WAVE', wave)
        #print('CLIENT', client)

        #Make this into multiple splits for other waves.

        self.absolute_wavepower[wave] = self._sum_ifsignal(args)
        self.relative_wavepower[wave] = self._compute_relative(wave, self.absolute_wavepower)

        for w, que in zip(self.waves, self.ques):
            if len(self.ques[w]) == self.window:
                que.popleft()
                que.append(self.relative_wavepower[w])
            else:
                que.append(self.relative_wavepower[w])

            output[w] = sum(que)/len(que)
        client.send_message('relative_wave', output)

    def _sum_ifsignal(self, args):
        sumVal = 0
        n = 0

        for i in range(4):
            if (self.hsi[i] == 1 or 2):
                sumVal += args[i]
                n += 1
        return sumVal/n

    @staticmethod
    def _compute_relative(wave, absolute_wavepower):
        return (math.pow(10, absolute_wavepower[wave]) / 
            (math.pow(10, absolute_wavepower[0]) +
            math.pow(10, absolute_wavepower[1]) +
            math.pow(10, absolute_wavepower[2]) +
            math.pow(10, absolute_wavepower[3]) +
            math.pow(10, absolute_wavepower[4]))) 
        
        

        