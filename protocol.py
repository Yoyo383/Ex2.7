import socket
import struct

PACK_FORMAT = 'I'
LENGTH_SIZE = 4


def send_data(sock, data):
    while data:
        count = sock.send(data)
        data = data[count:]


def send(sock, cmd, args):
    cmd_len = struct.pack(PACK_FORMAT, socket.htonl(len(cmd)))
    args_str = str(args)
    args_len = struct.pack(PACK_FORMAT, socket.htonl(len(args_str)))
    data = cmd_len + cmd.encode() + args_len + args_str.encode()
    send_data(sock, data)


def try_receive(sock, length):
    result = b''
    while len(result) < length:
        received = sock.recv(length - len(result))
        if not received:
            result = b''
            break
        result += received
    return result


def receive_part(sock):
    len_bytes = try_receive(sock, LENGTH_SIZE)
    len_int = socket.ntohl(struct.unpack(PACK_FORMAT, len_bytes)[0])
    return try_receive(sock, len_int).decode()


def receive(sock):
    cmd = receive_part(sock)
    data = receive_part(sock)
    return cmd, data
