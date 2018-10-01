#! /usr/bin/env python3

import socket
import os

import params
from framedSock import file_receive

switches_var_defaults = (
    (('-l', '--listenPort'), 'listenPort', 50001),
    (('-d', '--debug'), 'debug', False),  # boolean (set if present)
    (('-?', '--usage'), 'usage', False),  # boolean (set if present)
)

prog_name = 'file_server'
param_map = params.parse_params(switches_var_defaults)

debug, listenPort = param_map['debug'], param_map['listenPort']

if param_map['usage']:
    params.usage()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # listener socket
bind_addr = ('127.0.0.1', listenPort)
lsock.bind(bind_addr)
lsock.listen(5)
print('Listening on:', bind_addr)

while True:
    print('Waiting for connection')
    sock, addr = lsock.accept()
    print('Connection received from', addr)

    while True:
        data = file_receive(sock, debug=0)
        if data:
            filename, contents = data.values()
            if filename and contents:
                if not os.path.exists('serverFiles/' + filename):
                    downloaded_file = open('serverFiles/' + filename, 'wb')
                    downloaded_file.write(contents)
                    downloaded_file.close()
                    print('Downloaded file:', filename)
                else:
                    print('File already exists:', filename)
                continue
            else:
                print('Filename or contents empty')
        else:
            print('Connection ended with', addr)
            break
