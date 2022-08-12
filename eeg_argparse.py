"""This is essential for having two run."""

import argparse
from constants import DEFAULT_IP, DEFAULT_PORT

class EEG_argparse(object):

    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--SERVER_IP', type=str, required=False)
        self.parser.add_argument('--SERVER_PORT', type=int, required=False)
        self.parser.add_argument('--msg_prefix', type=str, required=False)
    
    def run_parser(self):
        args = self.parser.parse_args()
        
        if args.SERVER_IP == None:
            server_ip = DEFAULT_IP
        else:
            server_ip = args.SERVER_IP

        if args.SERVER_PORT == None:
                server_port = DEFAULT_PORT
        else:
            server_port = args.SERVER_PORT

        if args.msg_prefix == None:
            msg_prefix = None
        else:
            msg_prefix = args.msg_prefix
        
        return server_ip, server_port, msg_prefix

        