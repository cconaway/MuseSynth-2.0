import collections
import numpy as np
import math
import time

class ClientUtility(object):

    def send_to_clients(self, clients, send_address, output):
        for client in clients:
            client.send_message('{}'.format(send_address), output)
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

    def __init__(self, input_range, output_range, window=30, data_streams=3, send_address='/acc_xyz'):
        self.client_utility = ClientUtility()
        self.rangelimiter = RangeLimiter(input_range, output_range)

        self.send_address = send_address
        self.window = window
        self.directions = np.arange(data_streams)
        self.output = list(np.arange(data_streams))

        self.ques = []
        for i in range(data_streams):
            self.ques.append(collections.deque())

    def run(self, address: str, fixed_args, *args):

        for d, que in zip(self.directions, self.ques):
            if len(self.ques[0]) == self.window:
                que.popleft()
                que.append(args[d])

            else:
                que.append(args[d])
            self.output[d]= sum(que)/len(que)

        self.output = self.rangelimiter.squeeze(self.output)
        self.client_utility.send_to_clients(fixed_args[0], self.send_address, self.output)
        #clients[0].send_message('{}'.format(self.send_address), self.output)
        #time.sleep(1)



class RawEEGHandler(object):
    
    def __init__(self):
        self.send_address = '/raw_eeg'
        self.client_utility = ClientUtility()

    def run(self, address: str, fixed_args, *args):
        self.client_utility.send_to_clients(fixed_args[0], self.send_address, args)
        #client[0].send_message('{}'.format(self.send_address), args)



class WaveHandler(object):

    def __init__(self, input_range, output_range, window=30):
        self.client_utility = ClientUtility()
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

        self.absolute_wavepower[wave] = self._sum_ifsignal(args)
        self.relative_wavepower[wave] = self._compute_relative(wave, self.absolute_wavepower)

        for w, que in zip(self.waves, self.ques):
            if len(self.ques[w]) == self.window:
                que.popleft()
                que.append(self.relative_wavepower[w])
            else:
                que.append(self.relative_wavepower[w])

            output[w] = sum(que)/len(que) #This is dumb

        output = self.rangelimiter.squeeze(output)
        self.client_utility.send_to_clients(fixed_args[0], self.send_address, output)

    def _sum_ifsignal(self, args):
        sumVal = 0
        n = 0

        for i in range(4):
            if (self.hsi[i] == 1 or 2):
                sumVal += args[i]
                n += 1

        #put in if there is no signal.
        return sumVal/n

    @staticmethod
    def _compute_relative(wave, absolute_wavepower):
        return (math.pow(10, absolute_wavepower[wave]) / 
            (math.pow(10, absolute_wavepower[0]) +
            math.pow(10, absolute_wavepower[1]) +
            math.pow(10, absolute_wavepower[2]) +
            math.pow(10, absolute_wavepower[3]) +
            math.pow(10, absolute_wavepower[4]))) 
        
        

        