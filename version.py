# import os
# import threading
# import requests
# import shutil
# import subprocess
# import tkinter as tk
# from tkinter import ttk
# from config.env import MAIN_EXE, REMOTE_VERSION_URL, VERSION_FILE as LOCAL_VERSION

# # --- Simple log to console ---
# def log(msg):
#     print(msg)

# # --- Get remote version and path ---
# def get_remote_version_info():
#     try:
#         response = requests.get(REMOTE_VERSION_URL)
#         if response.status_code == 200:
#             data = response.json()
#             if data["status_code"] == 200 and data["content"]["data"]:
#                 latest = data["content"]["data"][0]
#                 return latest["version"], latest["path"]
#     except Exception as e:
#         log(f"❌ Failed to fetch remote version info: {e}")
#     return None, None

# # --- Version comparison ---
# def versions_different(local, remote):
#     return local.strip() != remote.strip()

# def show_progress_bar(download_func):
#     def wrapper(*args, **kwargs):
#         def download_in_thread():
#             try:
#                 download_func(*args, **kwargs, progress=progress_var)
#                 progress_window.after(0, progress_window.destroy)
#             except Exception as e:
#                 log(f"❌ Download error: {e}")
#                 progress_window.after(0, lambda: tk.messagebox.showerror("Download Failed", str(e)))
#                 progress_window.after(0, progress_window.destroy)

#         progress_window = tk.Tk()
#         progress_window.title("Downloading Update")
#         progress_window.geometry("400x100")
#         progress_window.resizable(False, False)

#         tk.Label(progress_window, text="Downloading new version...").pack(pady=10)
#         progress_var = tk.DoubleVar()
#         ttk.Progressbar(progress_window, length=300, variable=progress_var, maximum=100).pack(pady=5)

#         # Start download in a separate thread
#         threading.Thread(target=download_in_thread, daemon=True).start()

#         progress_window.mainloop()

#     return wrapper

# @show_progress_bar
# def copy_new_exe(source_path, progress):
#     total_size = os.path.getsize(source_path)
#     copied = 0
#     with open(source_path, "rb") as src, open("main_new.exe", "wb") as dst:
#         while chunk := src.read(1024 * 1024):
#             dst.write(chunk)
#             copied += len(chunk)
#             progress.set((copied / total_size) * 100)

# # --- Replace old EXE ---
# def replace_exe():
#     if os.path.exists(MAIN_EXE):
#         os.remove(MAIN_EXE)
#     shutil.move("main_new.exe", MAIN_EXE)
#     log("Replaced main.exe.")

# # --- Run EXE ---
# def run_main_exe():
#     log("Launching main.exe...")
#     subprocess.Popen([MAIN_EXE], shell=True)

# # --- Custom popup (instead of messagebox) ---
# def show_update_popup(current, latest):
#     popup = tk.Tk()
#     popup.title("Mandatory Update")
#     popup.geometry("400x200")
#     popup.resizable(False, False)

#     tk.Label(popup, text="A new version is available!", font=("Arial", 13, "bold")).pack(pady=10)
#     tk.Label(popup, text=f"Current Version: {current}", font=("Arial", 10)).pack()
#     tk.Label(popup, text=f"Latest Version: {latest}", font=("Arial", 10)).pack()
#     tk.Label(popup, text="Update is mandatory to continue.", font=("Arial", 10)).pack(pady=10)

#     tk.Button(popup, text="OK", command=popup.destroy, width=12).pack(pady=10)
#     popup.mainloop()

# # --- Main update logic ---
# def version_update():
#     remote_version, remote_path = get_remote_version_info()

#     if not remote_version or not remote_path:
#         log("Could not fetch version info. Running local version.")
#         run_main_exe()
#         return

#     if versions_different(LOCAL_VERSION, remote_version):
#         log(f"Update required: {LOCAL_VERSION} → {remote_version}")
#         show_update_popup(LOCAL_VERSION, remote_version)
#         copy_new_exe(remote_path)
#         replace_exe()
#         run_main_exe()
#     else:
#         log("Already using the latest version.")
#         run_main_exe()

############################################################################################

# import os
# import threading
# import requests
# import shutil
# import subprocess
# import tkinter as tk
# from tkinter import ttk
# from config.env import MAIN_EXE, REMOTE_VERSION_URL, VERSION_FILE as LOCAL_VERSION

# # --- Logging ---
# def log(msg):
#     print(msg)

# # --- Get remote version and path from API ---
# def get_remote_version_info():
#     try:
#         response = requests.get(REMOTE_VERSION_URL)
#         if response.status_code == 200:
#             data = response.json()
#             if data["status_code"] == 200 and data["content"]["data"]:
#                 latest = data["content"]["data"][0]
#                 return latest["version"], latest["path"]
#     except Exception as e:
#         log(f" Failed to fetch remote version info: {e}")
#     return None, None

# # --- Version comparison ---
# def versions_different(local, remote):
#     return local.strip() != remote.strip()

# # --- Replace main.exe with downloaded file ---
# def replace_exe():
#     if os.path.exists(MAIN_EXE):
#         os.remove(MAIN_EXE)
#     shutil.move("main_new.exe", MAIN_EXE)
#     log(" Replaced main.exe.")

# # --- Run main.exe ---
# def run_main_exe():
#     log(" Launching main.exe...")
#     #subprocess.Popen([MAIN_EXE], shell=True)

# # --- Custom popup before download ---
# def show_update_popup(current, latest):
#     popup = tk.Tk()
#     popup.title("Mandatory Update")
#     popup.resizable(False, False)
#     width, height = 400, 200
#     x = (popup.winfo_screenwidth() - width) // 2
#     y = (popup.winfo_screenheight() - height) // 2
#     popup.geometry(f"{width}x{height}+{x}+{y}")

#     tk.Label(popup, text="A new version is available!", font=("Arial", 13, "bold")).pack(pady=10)
#     tk.Label(popup, text=f"Current Version: {current}", font=("Arial", 10)).pack()
#     tk.Label(popup, text=f"Latest Version: {latest}", font=("Arial", 10)).pack()
#     tk.Label(popup, text="Update is mandatory to continue.", font=("Arial", 10)).pack(pady=10)

#     tk.Button(popup, text="OK", command=popup.destroy, width=12).pack(pady=10)
#     popup.mainloop()

# # --- Show progress bar while copying file ---
# def show_download_progress(source_path, on_complete):
#     def download():
#         try:
#             total_size = os.path.getsize(source_path)
#             copied = 0
#             with open(source_path, "rb") as src, open("main_new.exe", "wb") as dst:
#                 while chunk := src.read(1024 * 1024):
#                     dst.write(chunk)
#                     copied += len(chunk)
#                     percent = (copied / total_size) * 100
#                     progress_var.set(percent)
#                     percent_label_var.set(f"{percent:.1f}%")
#             window.after(0, lambda: [window.destroy(), on_complete()])
#         except Exception as e:
#             log(f"Error during copy: {e}")
#             window.after(0, lambda: [tk.messagebox.showerror("Error", str(e)), window.destroy()])

#     # Build UI
#     window = tk.Tk()
#     window.title("Downloading Update")
#     window.resizable(False, False)
#     width, height = 400, 150
#     x = (window.winfo_screenwidth() - width) // 2
#     y = (window.winfo_screenheight() - height) // 2
#     window.geometry(f"{width}x{height}+{x}+{y}")

#     tk.Label(window, text="Downloading new version...", font=("Arial", 11)).pack(pady=10)

#     progress_var = tk.DoubleVar()
#     ttk.Progressbar(window, length=300, variable=progress_var, maximum=100).pack(pady=5)

#     percent_label_var = tk.StringVar(value="0%")
#     tk.Label(window, textvariable=percent_label_var, font=("Arial", 10)).pack()

#     threading.Thread(target=download, daemon=True).start()
#     window.mainloop()

# # --- Main version update logic ---
# def version_update():
#     remote_version, remote_path = get_remote_version_info()

#     if not remote_version or not remote_path:
#         log("Could not fetch version info. Running local version.")
#         run_main_exe()
#         return

#     if versions_different(LOCAL_VERSION, remote_version):
#         log(f"Update required: {LOCAL_VERSION} → {remote_version}")
#         show_update_popup(LOCAL_VERSION, remote_version)
#         show_download_progress(
#             source_path=remote_path,
#             on_complete=lambda: [replace_exe(), run_main_exe()]
#         )
#     else:
#         log("Already using the latest version.")
#         run_main_exe()



#########################

import os
import threading
import requests
import shutil
import tkinter as tk
from tkinter import ttk, messagebox
from config.env import MAIN_EXE, REMOTE_VERSION_URL, VERSION_FILE as LOCAL_VERSION


# --- Logging ---
def log(msg):
    print(msg)


# --- Get remote version and path from API ---
def get_remote_version_info():
    try:
        response = requests.get(REMOTE_VERSION_URL)
        if response.status_code == 200:
            data = response.json()
            if data["status_code"] == 200 and data["content"]["data"]:
                latest = data["content"]["data"][0]
                return latest["version"], latest["path"]
    except Exception as e:
        log(f"❌ Failed to fetch remote version info: {e}")
    return None, None


# --- Version comparison ---
def versions_different(local, remote):
    return local.strip() != remote.strip()


# --- Replace main.exe with downloaded file ---
def replace_exe():
    try:
        if os.path.exists(MAIN_EXE):
            os.remove(MAIN_EXE)
        shutil.move("main_new.exe", MAIN_EXE)
        log("✅ Replaced main.exe.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to replace exe: {e}")


# --- Show progress bar while copying file ---
def show_download_progress(source_path, on_complete):
    def download():
        try:
            total_size = os.path.getsize(source_path)
            copied = 0
            with open(source_path, "rb") as src, open("main_new.exe", "wb") as dst:
                while chunk := src.read(1024 * 1024):
                    dst.write(chunk)
                    copied += len(chunk)
                    percent = (copied / total_size) * 100
                    progress_var.set(percent)
                    percent_text.set(f"{percent:.1f}%")
            window.after(0, lambda: [window.destroy(), on_complete()])
        except Exception as e:
            log(f"❌ Error during copy: {e}")
            window.after(0, lambda: [messagebox.showerror("Error", str(e)), window.destroy()])

    window = tk.Toplevel()
    window.title("Downloading Update")
    window.geometry("400x150")
    window.resizable(False, False)
    window.attributes("-topmost", True)
    window.lift()
    window.focus_force()
    x = (window.winfo_screenwidth() // 2) - 200
    y = (window.winfo_screenheight() // 2) - 75
    window.geometry(f"+{x}+{y}")

    tk.Label(window, text="Downloading new version...", font=("Arial", 12)).pack(pady=10)
   
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(window, length=300, variable=progress_var, maximum=100)
    progress_bar.pack(pady=5)

    percent_text = tk.StringVar(value="0%")
    tk.Label(window, textvariable=percent_text, font=("Arial", 10)).pack()

    threading.Thread(target=download, daemon=True).start()


# --- Show mandatory update popup ---
def show_update_popup(current, latest, on_confirm):
    popup = tk.Toplevel()
    popup.title("Mandatory Update")
    popup.geometry("400x200")
    popup.resizable(False, False)

    x = (popup.winfo_screenwidth() // 2) - 200
    y = (popup.winfo_screenheight() // 2) - 100
    popup.geometry(f"+{x}+{y}")

    popup.attributes("-topmost", True)
    popup.lift()
    popup.focus_force()

    tk.Label(popup, text="A new version is available!", font=("Arial", 13, "bold")).pack(pady=10)
    tk.Label(popup, text=f"Current Version: {current}", font=("Arial", 10)).pack()
    tk.Label(popup, text=f"Latest Version: {latest}", font=("Arial", 10)).pack()
    tk.Label(popup, text="Update is mandatory to continue.", font=("Arial", 10)).pack(pady=10)

    def confirm():
        popup.destroy()
        on_confirm()

    tk.Button(popup, text="OK", command=confirm, width=12).pack(pady=10)


# --- Main version update logic ---
def version_update(on_complete=None):
    remote_version, remote_path = get_remote_version_info()

    if not remote_version or not remote_path:
        log("⚠️ Could not fetch version info. Running local version.")
        if on_complete:
            on_complete()
        return

    if versions_different(LOCAL_VERSION, remote_version):
        log(f"🔄 Update required: {LOCAL_VERSION} → {remote_version}")
        root = tk.Tk()
        root.withdraw()  # hide root

        def proceed_download():
            show_download_progress(
                source_path=remote_path,
                on_complete=lambda: [replace_exe(), root.destroy(), on_complete() if on_complete else None]
            )

        show_update_popup(LOCAL_VERSION, remote_version, proceed_download)
        root.mainloop()

    else:
        log("✅ Already using the latest version.")
        if on_complete:
            on_complete()

