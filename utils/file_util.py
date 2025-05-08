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
