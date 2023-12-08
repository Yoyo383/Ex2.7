"""
Author: Yoad Winter
Date: 16.11.2023
Description: The server for exercise 2.7.
"""
import socket
from datetime import datetime, timedelta
import random
import os
import logging

QUEUE_LEN = 1
REQUEST_LEN = 4
SERVER_NAME = 'the yoyo server'
IP = '127.0.0.1'
PORT = 8000

SERVER_CLOSED_MSG = 'Server has closed, disconnecting.'

TIME_FORMAT = '%d.%m.%Y, %H:%M:%S'

LOG_FORMAT = '[%(levelname)s | %(asctime)s | %(processName)s] %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = LOG_DIR + '/server.log'


def return_time():
    """
    Returns current date and time.
    :return: Current date and time.
    :rtype: str
    """
    now = datetime.now()
    return now.strftime(TIME_FORMAT)


def return_name():
    """
    Returns the server name.
    :return: The server name.
    :rtype: str
    """
    return SERVER_NAME


def return_rand():
    """
    Returns a random number between 1 and 10.
    :return: A random number between 1 and 10.
    :rtype: int
    """
    return random.randint(1, 10)


def request_to_response(request):
    """
    Gets the request and returns the proper response.
    :param request: The request.
    :type request: str
    :return: The proper response.
    :rtype: str
    """
    if request == 'TIME':
        return return_time()

    elif request == 'NAME':
        return return_name()

    elif request == 'RAND':
        return str(return_rand())

    elif request == 'EXIT':
        return 'Exiting.'

    else:
        # not used anywhere because the input is valid (checked in client) but I still wanted to return something.
        return 'Invalid command.'


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


def protocolize_content(content):
    """
    Protocolizes the content as the following: the number of bytes, followed by a $ and then the content.
    :param content: The content.
    :type content: str
    :return: The message to send.
    :rtype: str
    """
    return str(len(content)) + '$' + content


def main_loop(client_socket):
    """
    The loop where the socket waits for a request, gets the proper response, and sends it. If the request is EXIT,
    the socket closes
    :param client_socket: The client socket.
    :type client_socket: socket.socket
    :return: Whether the server stays open after the client disconnects (returns False if received KeyboardInterrupt).
    :rtype: bool
    """
    result = True

    try:
        req = ''
        while req != 'EXIT':
            req = client_socket.recv(REQUEST_LEN).decode()
            logging.info(f'Client sent: {req}')

            response = request_to_response(req)
            message = protocolize_content(response)
            logging.debug(f'Response is: {response}, protocol is: {message}.')

            client_socket.send(message.encode())
            logging.info(f'Server sent: {message}')

        client_socket.close()
        print('Client disconnected.')
        logging.debug('Client disconnected, closing client socket.')

    except socket.error as err:
        logging.error('Client socket error: ' + str(err))
        print('Client socket error: ' + str(err))

    except KeyboardInterrupt:
        print('Keyboard interrupt detected, closing server.')
        client_socket.send(protocolize_content(SERVER_CLOSED_MSG).encode())
        logging.debug('Keyboard interrupt detected, closing server.')
        result = False

    finally:
        client_socket.close()
        logging.debug('Client socket closed.')
        return result


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
    for i in range(20):
        assert 1 <= return_rand() <= 10
    assert return_name() == SERVER_NAME
    # Checks if the time returned by return_time() is at most 1 second before the current time (to see if it returns
    # the correct time).
    assert datetime.strptime(return_time(), TIME_FORMAT) - datetime.now() <= timedelta(seconds=1)
    assert request_to_response('NAME') == SERVER_NAME
    assert request_to_response('EXIT') == 'Exiting.'
    assert protocolize_content('Do. Or do not. There is no try.') == '31$Do. Or do not. There is no try.'

    if not os.path.isdir(LOG_DIR):
        os.mkdir(LOG_DIR)
    logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)

    main()
