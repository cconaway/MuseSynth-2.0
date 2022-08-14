#Standard Library
import sys

#Third Party
from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher
from pythonosc.udp_client import SimpleUDPClient
from .eeg_proc import SplitWaveHandler

#Internal
from eeg_proc import MotionHandler, RawEEGHandler, WaveHandler
from range_parameters import ACC_INPUT, ACC_OUTPUT, GYRO_INPUT, GYRO_OUTPUT, ALLWAVE_INPUT, ALLWAVE_OUPUT
from eeg_argparse import EEG_argparse


def main():
    parser = EEG_argparse()
    server_ip, server_port, msg_prefix = parser.run_parser() #Check Constants for Defaults

    #Fill with clients if you want
    clients = [SimpleUDPClient('127.0.0.1', 8001), SimpleUDPClient('192.168.1.124', 8000)]

    #######################################################
    dispatch = Dispatcher()
    
    #Accelerometer
    acc = MotionHandler(input_range=ACC_INPUT, output_range=ACC_OUTPUT, window=2, msg_prefix=msg_prefix)
    dispatch.map("/muse/acc", acc.run, clients)

    #Gyroscope
    gyro = MotionHandler(send_address='/gyro_xyz', input_range=GYRO_INPUT, output_range=GYRO_OUTPUT, msg_prefix=msg_prefix)
    dispatch.map("/muse/gyro", gyro.run, clients)

    #RawEEG
    raw_eeg = RawEEGHandler(msg_prefix=msg_prefix, process_fft=False)
    dispatch.map("/muse/eeg", raw_eeg.run, clients)
    
    #Relative Wave Power
    wavehandler = WaveHandler(input_range=ALLWAVE_INPUT, output_range=ALLWAVE_OUPUT, msg_prefix=msg_prefix)
    dispatch.map("/muse/elements/horseshoe", wavehandler.run_hsi)
    wave_names = [('alpha_absolute',0),         
                    ('beta_absolute', 1),
                    ('gamma_absolute', 2),
                    ('delta_absolute', 3),
                    ('theta_absolute', 4)]           
    for wave in wave_names:
        dispatch.map(f"/muse/elements/{wave[0]}", wavehandler.run, clients, wave[1])

    #Sensor Split Alpha
    alphasplit = SplitWaveHandler(wavename='alpha', input_range=ALLWAVE_INPUT, output_range=ALLWAVE_OUPUT, msg_prefix=msg_prefix)
    dispatch.map("/muse/elements/alpha_absolute", alphasplit.run())
    #########################################################

    server = osc_server.ThreadingOSCUDPServer((server_ip, server_port), dispatch)
    print('Serving on {}:{}'.format(server_ip, server_port))
    print('Sending Messages to {}'. format(clients))
    if msg_prefix != None:
        print('Prefixing Messages with {}'.format(msg_prefix))
    server.serve_forever()

def shutdown():
    pass

if __name__ == "__main__":
    try: 
        main()
    except KeyboardInterrupt:
        shutdown()
