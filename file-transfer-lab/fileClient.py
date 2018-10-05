#! /usr/bin/env python3

import os
import re
import socket
import sys

import params
from framedSock import file_send

storage_dir = 'clientFiles/'  # directory used to send/receive files

switches_var_defaults = (
    (('-s', '--server'), 'server', '127.0.0.1:50001'),
    (('-d', '--debug'), 'debug', False),  # boolean (set if present)
    (('-?', '--usage'), 'usage', False),  # boolean (set if present)
)

prog_name = 'file_client'
param_map = params.parse_params(switches_var_defaults)
server, usage, debug = param_map['server'], param_map['usage'], param_map['debug']

if usage:
    params.usage()

try:
    server_host, server_port = re.split(':', server)
    server_port = int(server_port)
except:
    print('Could not parse server:port from ', server)
    sys.exit(1)

s = None
for res in socket.getaddrinfo(server_host, server_port, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, sock_type, proto, canon_name, sa = res
    try:
        print(f'Creating sock: af={af} type={sock_type} proto={proto}')
        s = socket.socket(af, sock_type, proto)
    except socket.error as msg:
        print(' Error: ', msg)
        s = None
        continue
    try:
        print(' Attempting to connect to', repr(sa))
        s.connect(sa)
    except socket.error as msg:
        print(' Error: ', msg)
        s.close()
        s = None
        continue
    break

if s is None:
    print('Could not open socket')
    sys.exit(1)

# print files available for sending, assume storage_dir is in same directory
print('Files available for sending:')
for file in os.listdir(storage_dir):
    print(' {} ({} bytes)'.format(file, os.path.getsize(storage_dir + file)))
print('Sending large files will take a while if you\'re stammering.')

while True:
    print('Enter file to send or \'exit\': ', end='')
    filename = input()
    if filename == 'exit':
        break
    if os.path.exists(storage_dir + filename):
        if file_send(s, filename, storage_dir):  # message sent successfully
            print(' File sent successfully')
        else:
            print(' Server closed, exiting')
            exit()
    else:
        print(' File does not exist')
