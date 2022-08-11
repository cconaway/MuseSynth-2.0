#Standard Library
import sys

#Third Party
from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher
from pythonosc.udp_client import SimpleUDPClient

#Internal
from eeg_proc import MotionHandler, RawEEGHandler, WaveHandler
from range_constants import ACC_INPUT, ACC_OUTPUT, GYRO_INPUT, GYRO_OUTPUT, ALLWAVE_INPUT, ALLWAVE_OUPUT

def main():
    server_ip = '169.254.40.240'
    server_port = 8000

    #Fill with clients if you want
    clients = [SimpleUDPClient('127.0.0.1', 8001)]

    #######################################################

    dispatch = Dispatcher()

    acc = MotionHandler(input_range=ACC_INPUT, output_range=ACC_OUTPUT)
    dispatch.map("/muse/acc", acc.run, clients)

    
    gyro = MotionHandler(send_address='/gyro_xyz', input_range=GYRO_INPUT, output_range=GYRO_OUTPUT)
    dispatch.map("/muse/gyro", gyro.run, clients)

    
    raw_eeg = RawEEGHandler()
    dispatch.map("/muse/eeg", raw_eeg.run, clients)
    
    wavehandler = WaveHandler(input_range=ALLWAVE_INPUT, output_range=ALLWAVE_OUPUT)
    dispatch.map("/muse/elements/horseshoe", wavehandler.run_hsi)
    wave_names = [('alpha_absolute',0),         
                    ('beta_absolute', 1),
                    ('gamma_absolute', 2),
                    ('delta_absolute', 3),
                    ('theta_absolute', 4)]
                    
    for wave in wave_names:
        dispatch.map(f"/muse/elements/{wave[0]}", wavehandler.run, clients, wave[1])
    
    #########################################################

    server = osc_server.ThreadingOSCUDPServer((server_ip, server_port), dispatch)
    print('Serving on {}:{}'.format(server_ip, server_port))
    print('Sending Messages to {}'. format(clients))
    server.serve_forever()

def shutdown():
    pass

if __name__ == "__main__":
    try: 
        main()
    except KeyboardInterrupt:
        shutdown()
