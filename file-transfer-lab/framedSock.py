import re

buff = b''
MAX_SIZE = 100  # max bytes to receive


def file_send(sock, filename):  # return the length of message after sending (length 0 indicates success)

    with open('clientFiles/' + filename, 'rb') as br:
        contents = br.read()

    # msg is in format <filename_length>:<filename><contents_length>:<contents>
    msg = str(len(filename)).encode() + b':' + filename.encode() + str(len(contents)).encode() + b':' + contents

    print(' Sending...', end='')
    try:
        while len(msg):
            bytes_sent = sock.send(msg[:MAX_SIZE])  # send MAX_SIZE bytes
            msg = msg[bytes_sent:]
        print('done')
    except BrokenPipeError:
        print('failed')
    return len(msg)


def file_receive(sock, debug=0):  # returns dictionary with filename and contents received TODO don't use dict
    filename_and_contents = {'fn': None, 'cn': None}
    global buff
    state = 'get_filename_len'
    filename_length = -1
    contents_length = -1
    while True:

        if state == 'get_filename_len':
            match = re.match(b'([^:]+):(.*)', buff, re.DOTALL | re.MULTILINE)  # look for colon
            if match:
                print(' Downloading...', end='')
                filename_len, buff = match.groups()
                try:
                    filename_length = int(filename_len)
                except ValueError:
                    if len(buff):
                        print('Badly formed filename length: ', filename_len)
                        return None
                state = 'get_filename'

        if state == 'get_filename':
            if len(buff) >= filename_length:
                filename_got = buff[0:filename_length]
                buff = buff[filename_length:]
                filename_and_contents['fn'] = filename_got.decode()  # store filename
                state = 'get_contents_len'

        if state == 'get_contents_len':
            match = re.match(b'([^:]+):(.*)', buff, re.DOTALL | re.MULTILINE)  # look for colon
            if match:
                contents_len, buff = match.groups()
                try:
                    contents_length = int(contents_len)
                except ValueError:
                    if len(buff):
                        print('Badly formed contents length: ', contents_len)
                        return None
                state = 'get_contents'

        if state == 'get_contents':
            if len(buff) >= contents_length:
                contents_got = buff[0:contents_length]
                buff = buff[contents_length:]
                filename_and_contents['cn'] = contents_got
                print('done')
                return filename_and_contents

        r = sock.recv(MAX_SIZE)  # receive MAX_SIZE bytes
        buff += r
        if len(r) == 0:
            if len(buff) != 0:
                print('Incomplete message')
            if debug:
                print(f'state={state} filename_length={filename_length} filename={filename_and_contents["fn"]} '
                      f'contents_length={contents_length}')
            return None
