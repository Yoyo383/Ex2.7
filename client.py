"""
Author: Yoad Winter
Date: 16.11.2023
Description: The client for exercise 2.7.
"""
import socket
import logging
import os
import protocol
import shlex

IP = '127.0.0.1'
PORT = 8080
COMMANDS = {'DIR': 1, 'DELETE': 1, 'COPY': 2, 'EXECUTE': 1, 'SCREENSHOT': 0, 'EXIT': 0}

SERVER_CLOSED_MSG = 'Server has closed, disconnecting.'

LOG_FORMAT = '[%(levelname)s | %(asctime)s | %(processName)s] %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = LOG_DIR + '/client.log'


def is_cmd_valid(cmd):
    """
    Checks if the entered command is valid.
    :param cmd: The command.
    :type cmd: str
    :return: Whether the command is valid.
    :rtype: bool
    """
    return cmd in COMMANDS.keys()


def main_loop(server_socket):
    """
    The user enters a command, if it's valid the client sends it and gets the response, then prints the response. If
    user enters EXIT, the client disconnects. Loops until user enters EXIT.
    :param server_socket: The socket.
    :type server_socket: socket.socket
    :return: None
    """
    cmd = ''
    while cmd != 'EXIT':
        req = shlex.split(input('ENTER COMMAND: ').replace('\\', '/'))

        if is_cmd_valid(req[0]):
            cmd, *args = req
            if len(args) != COMMANDS[cmd]:
                print(f'Expected {COMMANDS[cmd]} arguments but received {len(args)}.')
                continue
            protocol.send(server_socket, cmd, args)
            logging.info(f'Client sent: {req}')

            response = protocol.receive(server_socket)
            logging.info(f'Server sent: {response}')
            print(response[1])
            if response[1] == SERVER_CLOSED_MSG:
                logging.debug(f'Server closed, client disconnected.')
                break
        else:
            logging.warning(f'Client entered invalid command: {req}')
            print('Invalid command! Enter one of the following commands: TIME | NAME | RAND | EXIT')


def main():
    """
    The main function.
    :return: None.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logging.debug('Server socket created.')

    try:
        server_socket.connect((IP, PORT))
        logging.debug('Socket connected to server.')
        print('Connected to server!')
        main_loop(server_socket)

    except socket.error as err:
        logging.error('Socket error: ' + str(err))
        print('Socket error: ' + str(err))

    except KeyboardInterrupt:
        protocol.send(server_socket, 'EXIT', [])
        logging.debug('Keyboard interrupt detected from client, disconnecting from server.')

    finally:
        server_socket.close()
        logging.debug('Server socket closed.')


if __name__ == '__main__':
    if not os.path.isdir(LOG_DIR):
        os.mkdir(LOG_DIR)
    logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)

    main()
