#Standard Library
import sys

#Third Party
from pythonosc import osc_server
from pythonosc.dispatcher import Dispatcher
from pythonosc.udp_client import SimpleUDPClient

#Internal
from eeg_proc import MotionHandler, RawEEGHandler, WaveHandler

def main():
    ip = '192.168.0.55'
    port = 8000
    client = SimpleUDPClient('127.0.0.1', 8001)

    #######################################################

    dispatch = Dispatcher()

    acc = MotionHandler()
    dispatch.map("/muse/acc", acc.run, client)

    gyro = MotionHandler(send_address='gyro_xyz')
    dispatch.map("/muse/gyro", gyro.run, client)

    
    raw_eeg = RawEEGHandler()
    dispatch.map("/muse/eeg", raw_eeg.run, client)
    
    wavehandler = WaveHandler()
    dispatch.map("/muse/elements/horseshoe", wavehandler.run_hsi)
    wave_names = [('alpha_absolute',0),         
                    ('beta_absolute', 1),
                    ('gamma_absolute', 2),
                    ('delta_absolute', 3),
                    ('theta_absolute', 4)]
    for wave in wave_names:
        dispatch.map(f"/muse/elements/{wave[0]}", wavehandler.run, client, wave[1])
    
    #########################################################

    server = osc_server.ThreadingOSCUDPServer((ip, port), dispatch)
    print('Serving on {}:{}'.format(ip, port))
    server.serve_forever()

def shutdown():
    pass

if __name__ == "__main__":
    try: 
        main()
    except KeyboardInterrupt:
        shutdown()
