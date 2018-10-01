#! /usr/bin/env python3

import os
import re
import socket
import sys

import params
from framedSock import file_send

files_dir = 'clientFiles'  # assuming in same directory

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

print('Files available for upload:')
for file in os.listdir(files_dir + '/'):
    print(f' {file} ({os.path.getsize(files_dir + "/" + file)} bytes)')

while True:
    print('Enter filename to upload or \'exit\': ', end='')
    filename = input()
    if filename == 'exit':
        break
    if os.path.exists('clientFiles/' + filename):
        file_send(s, filename)
    else:
        print(' File does not exist')
