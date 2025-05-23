import os
import sys

def resource_path(relative_path):
    """ Get the absolute path to the resource (works for EXE). """
    if getattr(sys, 'frozen', False):
        # If running as a PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, "assets", relative_path)

def resource_path_for_env(relative_path):
    """Get absolute path to resource (works for dev and PyInstaller)"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.abspath(relative_path)

