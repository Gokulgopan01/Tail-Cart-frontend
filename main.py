import winreg as reg
from app import Application

def is_protocol_registered(protocol_name):
    
    try:
        reg.OpenKey(reg.HKEY_CLASSES_ROOT, f"{protocol_name}\\shell\\open\\command")
        print("Already registered")
        return True
    except FileNotFoundError:
        print("Not registered")
        return False

def register_url_protocol(protocol_name, exe_path):
    key_path = f"{protocol_name}\\shell\\open\\command"
    full_command = f'"{exe_path}" "%1"'

    try:
        print(f"Registering protocol: {protocol_name} with command: {full_command}")
        reg.CreateKey(reg.HKEY_CLASSES_ROOT, protocol_name)
        reg.SetValue(reg.HKEY_CLASSES_ROOT, protocol_name, reg.REG_SZ, "URL Protocol")
        reg_key = reg.OpenKey(reg.HKEY_CLASSES_ROOT, protocol_name, 0, reg.KEY_SET_VALUE)
        reg.SetValueEx(reg_key, "URL Protocol", 0, reg.REG_SZ, "")
        reg_key.Close()

        reg.CreateKey(reg.HKEY_CLASSES_ROOT, f"{protocol_name}\\shell")
        reg.CreateKey(reg.HKEY_CLASSES_ROOT, f"{protocol_name}\\shell\\open")
        reg.CreateKey(reg.HKEY_CLASSES_ROOT, key_path)
        reg.SetValue(reg.HKEY_CLASSES_ROOT, key_path, reg.REG_SZ, full_command)

        print(f"Registered URL protocol: {protocol_name}")
    except Exception as e:
        print(f"Failed to register protocol: {e}")

if __name__ == "__main__":
    protocol_name = "hybridbpoautologinv1"
    #exe_path = r"S:\HybridBPO\autologin\dist\main.exe"
    exe_path = r"C:\HybridBPO\autologin\dist\main.exe"
    if not is_protocol_registered(protocol_name):
        register_url_protocol(protocol_name, exe_path)
    else:
        print(f"Protocol '{protocol_name}' is already registered.")

    app = Application()
    app.mainloop()


