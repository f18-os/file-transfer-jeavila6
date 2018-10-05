import re
import sys

buff = b''
MAX_SIZE = 100  # max num of bytes to send/receive


def file_send(sock, filename, storage_dir):  # send file to server, return True on success
    with open(storage_dir + filename, 'rb') as br:
        contents = br.read()
    # msg is in format <filename_length>:<filename><contents_length>:<contents>
    msg = str(len(filename)).encode() + b':' + filename.encode() + str(len(contents)).encode() + b':' + contents
    try:
        while len(msg):
            bytes_sent = sock.send(msg[:MAX_SIZE])  # send MAX_SIZE bytes
            msg = msg[bytes_sent:]
    except BrokenPipeError:
        return False
    return True


def file_receive(sock):  # receive file from client, return tuple with filename and contents

    global buff
    state = 'get_filename_len'
    filename_length = -1
    contents_length = -1
    filename = ''
    while True:

        if state == 'get_filename_len':  # state 0: reading filename length
            match = re.match(b'([^:]+):(.*)', buff, re.DOTALL | re.MULTILINE)  # look for colon
            if match:
                print(' Receiving file...')
                filename_len, buff = match.groups()
                try:
                    filename_length = int(filename_len)
                except ValueError:
                    if len(buff):
                        print(' Badly formed filename length: ', filename_len)
                        return None
                state = 'get_filename'

        if state == 'get_filename':  # state 1: reading filename
            if len(buff) >= filename_length:
                filename_encoded = buff[0:filename_length]
                buff = buff[filename_length:]
                filename = filename_encoded.decode()
                state = 'get_contents_len'

        if state == 'get_contents_len':  # state 2: reading contents length
            match = re.match(b'([^:]+):(.*)', buff, re.DOTALL | re.MULTILINE)  # look for colon
            if match:
                contents_len, buff = match.groups()
                try:
                    contents_length = int(contents_len)
                except ValueError:
                    if len(buff):
                        print(' Badly formed contents length: ', contents_len)
                        return None
                state = 'get_contents'

        if state == 'get_contents':  # state 3: reading contents
            if len(buff) >= contents_length:
                contents = buff[0:contents_length]
                buff = buff[contents_length:]
                return filename, contents

        r = sock.recv(MAX_SIZE)  # receive MAX_SIZE bytes
        buff += r
        if len(r) == 0:  # nothing to receive
            if len(buff) != 0:
                print(' Incomplete message')
            return None
