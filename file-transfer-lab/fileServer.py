#! /usr/bin/env python3

import os
import socket
import sys

import params
from framedSock import file_receive

storage_dir = 'serverFiles/'  # directory used to send/receive files
if not os.path.exists(storage_dir):
    os.makedirs(storage_dir)

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
    sock, addr = lsock.accept()
    print('Connection received from', addr)

    try:
        ret_val = os.fork()
    except OSError as e:
        print('Fork failed:', e, file=sys.stderr)
        continue

    if ret_val:  # child handles connection, parent waits for a new one
        continue

    while True:
        data = file_receive(sock)
        if data:
            filename, contents = data
            if filename and contents:  # file received successfully
                if os.path.exists(storage_dir + filename):
                    print(' File already exists:', filename)
                else:
                    with open(storage_dir + filename, 'wb') as file:
                        file.write(contents)
                    print(' Downloaded file:', filename)
                continue
            else:
                print(' Filename or contents empty')
        else:
            print('Connection ended with', addr)
            exit()
