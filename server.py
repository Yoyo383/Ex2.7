"""
Author: Yoad Winter
Date: 9.12.2023
Description: The server for exercise 2.7.
"""
import shutil
import socket
import os
import logging
import protocol
import server_funcs

QUEUE_LEN = 1
IP = '127.0.0.1'
PORT = 8080

SERVER_CLOSED_MSG = 'Server has closed, disconnecting.'

CWD = os.getcwd().replace('\\', '/')
TEST_FOLDER = CWD + '/test'
FIRST_FILE = '/sand_rant.txt'
SECOND_FILE = '/sand_rant2.txt'

LOG_FORMAT = '[%(levelname)s | %(asctime)s | %(processName)s] %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = LOG_DIR + '/server.log'


def execute_command(cmd, data):
    """
    Executes the command with the given arguments.
    :param cmd: The command.
    :type cmd: str
    :param data: The arguments as a string in the following format: "(param1, param2, ...)"
    :type data: str
    :return: The result of the command.
    :rtype: str
    """
    # gets the function from server_funcs using getattr()
    cmd_func = getattr(server_funcs, f'func_{cmd.lower()}')
    # convert data into a tuple (or a string if it's just one argument) using eval().
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

    # prepare for asserts
    os.mkdir(TEST_FOLDER)
    with open(TEST_FOLDER + FIRST_FILE, 'w') as f:
        f.write("I Don't Like Sand. It's Coarse And Rough And Irritating, And It Gets Everywhere.")

    try:
        assert execute_command('DIR', f"('{TEST_FOLDER}')") == TEST_FOLDER + FIRST_FILE
        assert (execute_command('COPY', f"('{TEST_FOLDER + FIRST_FILE}', '{TEST_FOLDER + SECOND_FILE}')") ==
                f"Successfully copied '{TEST_FOLDER + FIRST_FILE}' into '{TEST_FOLDER + SECOND_FILE}'.")
        assert (execute_command('DELETE', f"('{TEST_FOLDER + SECOND_FILE}')") ==
                f"Deleted '{TEST_FOLDER + SECOND_FILE}'.")
    except AssertionError as error:
        raise error
    finally:
        shutil.rmtree(TEST_FOLDER)

    if not os.path.isdir(LOG_DIR):
        os.mkdir(LOG_DIR)
    logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)

    main()
