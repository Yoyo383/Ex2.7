"""
Author: Yoad Winter
Date: 16.11.2023
Description: The server for exercise 2.7.
"""
import socket
import os
import logging
import protocol
import server_funcs
import signal
import sys

QUEUE_LEN = 1
REQUEST_LEN = 4
IP = '127.0.0.1'
PORT = 8080

SERVER_CLOSED_MSG = 'Server has closed, disconnecting.'

LOG_FORMAT = '[%(levelname)s | %(asctime)s | %(processName)s] %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = LOG_DIR + '/server.log'


def execute_command(cmd, data):
    cmd_func = getattr(server_funcs, f'func_{cmd.lower()}')
    return cmd_func(eval(data))


def connect_socket(server_socket):
    """
    Binds and connects the socket.
    :param server_socket: The socket.
    :type server_socket: socket.socket
    :return: None.
    """
    server_socket.bind((IP, PORT))
    logging.debug(f'Socket bound to: {IP}:{PORT}')
    server_socket.listen(QUEUE_LEN)
    logging.debug(f'Socket is listening with a queue length of {QUEUE_LEN}.')


def connect_to_client(server_socket):
    """
    Waits for client to connect and returns the socket.
    :param server_socket: The server socket.
    :type server_socket: socket.socket
    :return: The client socket.
    :rtype: socket.socket
    """
    print('Waiting for client to connect...')
    logging.debug('Waiting for client to connect...')
    client_socket, client_addr = server_socket.accept()
    logging.debug('Established connection with client.')
    print('Client connected!')
    return client_socket


def main_loop(client_socket):
    """
    The loop where the socket waits for a request, gets the proper response, and sends it. If the request is EXIT,
    the socket closes
    :param client_socket: The client socket.
    :type client_socket: socket.socket
    :return: Whether the server stays open after the client disconnects (returns False if received KeyboardInterrupt).
    :rtype: bool
    """
    try:
        cmd = ''
        while cmd != 'EXIT':
            req = protocol.receive(client_socket)
            logging.info(f'Client sent: {req}')

            cmd, data = req
            response = execute_command(cmd, data)
            protocol.send(client_socket, cmd, response)

        client_socket.close()
        print('Client disconnected.')
        logging.debug('Client disconnected, closing client socket.')

    except socket.error as err:
        logging.error('Client socket error: ' + str(err))
        print('Client socket error: ' + str(err))

    except KeyboardInterrupt:
        print('Keyboard interrupt detected, closing server.')
        protocol.send(client_socket, 'EXIT', SERVER_CLOSED_MSG)
        logging.debug('Keyboard interrupt detected, closing server.')
        return False

    finally:
        client_socket.close()
        logging.debug('Client socket closed.')

    return True


def connect_client_loop(server_socket):
    """
    The server waits for a client and does the main loop. When the client disconnects, the server waits for another one
    unless the main loop sent that the server is closing.
    :param server_socket: The server socket.
    :type server_socket: socket.socket
    :return: None.
    """
    result = True
    while result:
        client_socket = connect_to_client(server_socket)
        result = main_loop(client_socket)


def main():
    """
    The main function.
    :return: None.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logging.debug('Server socket created.')

    try:
        connect_socket(server_socket)
        connect_client_loop(server_socket)

    except socket.error as err:
        logging.error('Server socket error: ' + str(err))
        print('Server socket error: ' + str(err))

    except KeyboardInterrupt:
        logging.error('Keyboard interrupt detected, closing server.')
        print('Keyboard interrupt detected, closing server.')

    finally:
        server_socket.close()
        logging.debug('Server socket closed.')


if __name__ == '__main__':
    if not os.path.isdir(LOG_DIR):
        os.mkdir(LOG_DIR)
    logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)

    main()
