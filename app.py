
import ctypes
import os
import time
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from utils.helper import center_window, params_check
from utils.file_util import resource_path
from tkinter import PhotoImage
# from utils import user_data
from screens.Portal_Instruction_Screen import PortalInstructionScreen
from screens.ecesis_login_screen import EcesisLoginScreen
from screens.entry_screen import EntryScreen
from screens.profile_screen import ProfileScreen
from utils.glogger import GLogger
import pyi_splash

logger = GLogger()

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
        process_type, hybrid_orderid, hybrid_token = params_check()
        # process_type="SmartEntry"
        #process_type="PortalLogin"
        # process_type="AutoLogin"
        logger.log(
            module="Application-route_startup",
            order_id=hybrid_orderid,
            action_type="Info",
            remarks=f"Params: process_type={process_type}, hybrid_orderid={hybrid_orderid}",
            severity="INFO"
        )
        # login_data = user_data.load_login_data()
        # print("Login data:", login_data)

        if process_type == "SmartEntry":
            self.show_frame("EntryScreen")
        elif process_type == "PortalLogin":
            self.show_frame("PortalInstructionScreen")
        # elif login_data.get("logged_in"):
        #     self.show_frame("EcesisLoginScreen")
        elif process_type == "AutoLogin":
            self.show_frame("EcesisLoginScreen")
        else:
            self.show_frame("EcesisLoginScreen")

    def show_frame(self, page_name):
        """Bring the requested screen to the front."""
        frame = self.frames.get(page_name)
        if frame:
            logger.log(
                module="Application-show_frame",
                action_type="Navigation",
                remarks=f"Switching to frame: {page_name}",
                severity="INFO"
            )
            frame.tkraise()
    def set_icon(self):
        self.iconphoto(False, self.logo)
    






