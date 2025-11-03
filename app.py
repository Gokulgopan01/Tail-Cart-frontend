import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from utils.helper import center_window, get_saved_token, params_check
from utils.file_util import resource_path
from tkinter import PhotoImage
from utils import user_data
from screens.Portal_Instruction_Screen import PortalInstructionScreen
from screens.ecesis_login_screen import EcesisLoginScreen
from screens.entry_screen import EntryScreen
from screens.profile_screen import ProfileScreen
import pyi_splash

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ECESIS - Login")
        self.geometry("800x650")
        self.resizable(True, True)
        center_window(self, 800, 650)
        # Load logo and set icon
        img_path = resource_path("logo.jpg")
        image = Image.open(img_path).resize((100, 100))
        self.logo = ImageTk.PhotoImage(image)
        #self.iconphoto(False, self.logo)
        self.after(200, self.set_icon)
        pyi_splash.close()

        # Load image
        # img_path = resource_path("logo.jpg")
        # try:
        #     image = Image.open(img_path).resize((64, 64))
        #     self.icon_image = ImageTk.PhotoImage(image)  # store as instance variable
        #     self.iconphoto(False, self.icon_image)
        # except Exception as e:
        #     print("Failed to load image:", e)

        # Bring to front briefly
        self.lift()
        self.attributes('-topmost', True)
        self.after(1000, lambda: self.attributes('-topmost', False))

        self.configure(bg="#FFFFFF")

        # Theme and styles
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#FFFFFF")
        self.style.configure("TLabel", foreground="black", font=("Arial", 11))
        self.style.configure("Title.TLabel", foreground="#4285F4", font=("Arial", 14, "bold"))
        self.style.configure("Welcome.TLabel", foreground="black", font=("Arial", 14, "bold"))
        self.style.configure("TLabelFrame", borderwidth=2, relief="solid")
        self.style.configure("TLabelFrame.Label", foreground="#4285F4", font=("Arial", 12, "bold"))
        self.style.configure("TButton", font=("Arial", 12, "bold"), padding=5, background="#1E90FF", foreground="white")

        # Frame container setup
        self.frames = {}
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Register frames
        for F in (EcesisLoginScreen, EntryScreen, ProfileScreen, PortalInstructionScreen):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Determine startup screen
        self.route_startup()

    def route_startup(self):
        """Decide which screen to show based on input parameters or login status."""
        arg1, arg2, arg3 = params_check()
        arg1="SmartEntry"
        #arg1="PortalLogin"
        #arg1="AutoLogin"
        print(f"Params: arg1={arg1}, arg2={arg2}, arg3={arg3}")
        login_data = user_data.load_login_data()
        print("Login data:", login_data)

        if arg1 == "SmartEntry":
            self.show_frame("EntryScreen")
        elif arg1 == "PortalLogin":
            self.show_frame("PortalInstructionScreen")
        # elif login_data.get("logged_in"):
        #     self.show_frame("EcesisLoginScreen")
        elif arg1 == "AutoLogin":
            self.show_frame("EcesisLoginScreen")
        else:
            self.show_frame("EcesisLoginScreen")

    def show_frame(self, page_name):
        """Bring the requested screen to the front."""
        frame = self.frames.get(page_name)
        if frame:
            print(f"Switching to frame: {page_name}")
            frame.tkraise()
    def set_icon(self):
        self.iconphoto(False, self.logo)