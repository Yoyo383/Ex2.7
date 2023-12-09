import glob
import os
import shutil
import subprocess
import pyautogui


def func_dir(path):
    if not os.path.isdir(path):
        return f"'{path}' is not a directory."
    files = glob.glob(f'{path}/*.*')  # using / instead of \ so it could also work on Mac and Linux.
    return '\n'.join(files)


def func_delete(path):
    if not os.path.isfile(path):
        return f"'{path}' does not exist."
    # since I know that path must exist (because of the if statement), I don't need to try/except.
    os.remove(path)
    return f"Deleted '{path}'."


def func_copy(paths):
    source, destination = paths
    if not os.path.isfile(source):
        return f"'{source}' does not exist."
    try:
        shutil.copy(source, destination)
        return f"Successfully copied '{source}' into '{destination}'."
    except (PermissionError,  shutil.SameFileError):
        return f"Failed to copy '{source}' into '{destination}'."


def func_execute(path):
    if not os.path.isfile(path):
        return f"'{path}' does not exist."
    try:
        subprocess.call(path)
        return f"Successfully executed '{path}'."
    except OSError:
        return f"Could not execute '{path}'."


def func_screenshot(param):
    image = pyautogui.screenshot()
    image.save('image.jpg')
    return f"'{image.mode}', {image.size}, {image.tobytes()}"


def func_exit(param):
    return 'Exiting.'
