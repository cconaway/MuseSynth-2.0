Hello!

This is an intermediary layer for using the MUSE EEG headset with different OSC devices. With this you can define ranges of values to normalize to, send to multiple clients, define servers,
and add layers of processing to the MUSE headset data out. Unfortunetely Muse has not open-sourced their SDK so one still has to get their hands on the old 32bit version or MindMoniter (a paid SDK).

To install:
    1. Clone this Repository
    2. $pip install python-osc 
    3. If using the fft processor install numpy and scipy.signal

To use:
    1. Go to server_constants.py and put in your preferred ip and port.
    2. Go to function_config.py and select which functions you want on and serving.
    3. Go to range_parameters and put in your preffered output ranges.
    4. $python3 main.py

Other Commands and flags:
    --SERVER_PORT: Define a non-default server port
    --SERVER_IP: Define a non-default server ip
    -prefix: Add a message prefix to OSC send to the clients.
