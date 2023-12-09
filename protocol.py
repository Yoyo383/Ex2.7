"""
Author: Yoad Winter
Date: 9.12.2023
Description: The protocol functions.
"""
import socket
import struct

PACK_FORMAT = 'I'
LENGTH_SIZE = 4


def send_data(sock, data):
    """
    Sends the data through the socket. Exists in case the data is too long and one send() won't be able to send it all.
    :param sock: The socket.
    :type sock: socket.socket
    :param data: The data to send.
    :type data: bytes
    :return: None.
    """
    while data:
        count = sock.send(data)
        data = data[count:]


def send(sock, cmd, args):
    """
    Takes a socket, command and arguments. Sends the command and arguments through the socket using the protocol
    described in README.md.
    :param sock: The socket.
    :type sock: socket.socket
    :param cmd: The command.
    :type cmd: str
    :param args: The arguments as a string, represented like this: "(param1, param2, ...)"
    :type args: str
    :return: None.
    """
    cmd_len = struct.pack(PACK_FORMAT, socket.htonl(len(cmd)))
    args_len = struct.pack(PACK_FORMAT, socket.htonl(len(args)))
    data = cmd_len + cmd.encode() + args_len + args.encode()
    send_data(sock, data)


def receive_with_length(sock, length):
    """
    Receives data of certain length from a socket.
    :param sock: The socket.
    :type sock: socket.socket
    :param length: Length of data.
    :type length: int
    :return: The received data.
    :rtype: bytes
    """
    result = b''
    while len(result) < length:
        received = sock.recv(length - len(result))
        if not received:
            result = b''
            break
        result += received
    return result


def receive_part(sock):
    """
    Receives LENGTH_SIZE bytes, turns them into an int that represents the length of the data, and then receives that
    data.
    :param sock: The socket.
    :type sock: socket.socket
    :return: The data received (without the length).
    :rtype: str
    """
    len_bytes = receive_with_length(sock, LENGTH_SIZE)
    len_int = socket.ntohl(struct.unpack(PACK_FORMAT, len_bytes)[0])
    return receive_with_length(sock, len_int).decode()


def receive(sock):
    """
    Receives data from the socket using the protocol described in README.md.
    :param sock: The socket.
    :type sock: socket.socket
    :return: A tuple in the following format: (cmd, data).
    :rtype: tuple[str, str]
    """
    cmd = receive_part(sock)
    data = receive_part(sock)
    return cmd, data
