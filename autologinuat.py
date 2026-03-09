from datetime import datetime
import logging
import sys, os
import subprocess
import winreg as reg
from app import Application

# from utils.glogger import send_log_sync
from version import version_update
  



# --- Check if protocol is already registered ---
def is_protocol_registered(protocol_name):
    try:
        reg.OpenKey(reg.HKEY_CURRENT_USER, f"Software\\Classes\\{protocol_name}\\shell\\open\\command")
        print(f" Protocol '{protocol_name}' is already registered.")
        return True
    except FileNotFoundError:
        print(f" Protocol '{protocol_name}' not registered.")
        return False

# --- Register URL protocol in HKCU (no admin required) ---
def register_url_protocol(protocol_name, exe_path):
    base_path = f"Software\\Classes\\{protocol_name}"
    command = f'"{exe_path}" "%1"'

    try:
        print(f" Registering protocol: {protocol_name} -> {command}")
        # Create protocol root
        reg.CreateKey(reg.HKEY_CURRENT_USER, base_path)
        reg.SetValue(reg.HKEY_CURRENT_USER, base_path, reg.REG_SZ, "URL Protocol")

        with reg.OpenKey(reg.HKEY_CURRENT_USER, base_path, 0, reg.KEY_SET_VALUE) as key:
            reg.SetValueEx(key, "URL Protocol", 0, reg.REG_SZ, "")

        # Create command path
        reg.CreateKey(reg.HKEY_CURRENT_USER, f"{base_path}\\shell")
        reg.CreateKey(reg.HKEY_CURRENT_USER, f"{base_path}\\shell\\open")
        reg.CreateKey(reg.HKEY_CURRENT_USER, f"{base_path}\\shell\\open\\command")
        reg.SetValue(reg.HKEY_CURRENT_USER, f"{base_path}\\shell\\open\\command", reg.REG_SZ, command)

        print(f" Protocol '{protocol_name}' registered successfully (HKCU).")
    except Exception as e:
        print(f" Failed to register protocol: {e}")

def launch_app():
    # Step 2: Register protocol (if not already registered)
    protocol_name = "UAThybridbpoautologin"
    #protocol_name = "hybridbpoautologinv1"
    # desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

    # exe_path = desktop_path + r"\main.exe"

    exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
    print("exepath",exe_path)

    
    # if not is_protocol_registered(protocol_name):
    #     register_url_protocol(protocol_name, exe_path)
    register_url_protocol(protocol_name, exe_path)
    # # Step 3: Start application
    app = Application()
    app.mainloop()

    

if __name__ == "__main__":
    # Step 1: Run version check first, then launch_app
    # version_update(lambda: Application().mainloop())
    # launch_app()
    version_update(launch_app) 



