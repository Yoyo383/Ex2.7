"""
Author: Yoad Winter
Date: 9.12.2023
Description: The command functions for the server.
"""
import glob
import os
import shutil
import subprocess
import pyautogui

IMAGE_PATH = 'image.jpg'


def func_dir(path):
    """
    Takes a path and shows the directory's content.
    :param path: The path of the directory.
    :type path: str
    :return: Content of directory.
    :rtype: str
    """
    if not os.path.isdir(path):
        return f"'{path}' is not a directory."
    files = glob.glob(f'{path}/*.*')  # using / instead of \ so it could also work on Mac and Linux.
    return '\n'.join(files)


def func_delete(path):
    """
    Takes a path and deletes the file.
    :param path: The file path.
    :type path: str
    :return: The response (whether the file was deleted or not).
    :rtype: str
    """
    if not os.path.isfile(path):
        return f"'{path}' does not exist."
    try:
        os.remove(path)
        return f"Deleted '{path}'."
    except OSError:
        return f"Could not delete '{path}'."


def func_copy(paths):
    """
    Takes two paths and copies the first one to the second one.
    :param paths: A tuple of the paths in the following form: (source, destination).
    :type paths: tuple[str, str]
    :return: The response (whether the file was copied or not).
    :rtype: str
    """
    source, destination = paths
    if not os.path.isfile(source):
        return f"'{source}' does not exist."
    try:
        shutil.copy(source, destination)
        return f"Successfully copied '{source}' into '{destination}'."
    except (PermissionError,  shutil.SameFileError):
        return f"Failed to copy '{source}' into '{destination}'."


def func_execute(path):
    """
    Takes a path and executes the program at the path.
    :param path: The path to the executable.
    :type path: str
    :return: The response (whether the file was executed or not).
    :rtype: str
    """
    if not os.path.isfile(path):
        return f"'{path}' does not exist."
    try:
        subprocess.call(path)
        return f"Successfully executed '{path}'."
    except OSError:
        return f"Could not execute '{path}'."


def func_screenshot(param):
    """
    Takes a screenshot and saves it to IMAGE_PATH.
    :param param: Unused parameter, used for symmetry.
    :return: A string in the following format: "'<mode>', <size tuple>, <bytes>"
    :rtype: str
    """
    image = pyautogui.screenshot()
    image.save(IMAGE_PATH)
    return f"'{image.mode}', {image.size}, {image.tobytes()}"


def func_exit(param):
    """
    Returns 'Exiting.'
    :param param: Unused parameter, used for symmetry.
    :return: 'Exiting.'
    :rtype: str
    """
    return 'Exiting.'
