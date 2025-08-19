# import sys
# import tkinter as tk
# from tkinter import Image, ttk
# from screens.Portal_Instruction_Screen import PortalInstructionScreen
# from screens.ecesis_login_screen import EcesisLoginScreen
# from screens.entry_screen import EntryScreen
# from screens.settings_screen import SettingsScreen
# from urllib.parse import urlparse, parse_qs
# from utils.helper import center_window, get_saved_token, params_check
# from utils.file_util import resource_path
# from PIL import Image, ImageDraw, ImageTk
# from utils import user_data
# from screens.profile_screen import ProfileScreen
# class Application(tk.Tk):
#     def __init__(self): #root passed but not used.
#         super().__init__() #super init.
#         self.title("ECESIS - Login")
#         self.geometry("800x650") #corrected geometry.
#         self.resizable(True, True)
#         # Center the window
#         center_window(self, 800, 650)
#         img_path = resource_path("logo.jpg")
#         image = Image.open(img_path)
#         image = image.resize((100, 100))  # Resize if needed
#         self.logo = ImageTk.PhotoImage(image)
#         # Set the window icon
#         self.iconphoto(False, self.logo)  # False ensures the icon applies to all windows
#         # Bring the window to the front
#         self.lift()
#         self.attributes('-topmost', True)
#         self.after(1000, lambda: self.attributes('-topmost', False))

#         # Apply background color
#         self.configure(bg="#FFFFFF")  # White background

#         # Define styles
#         self.style = ttk.Style()

#         # Set background color for frames
#         self.style.configure("TFrame", background="#FFFFFF")  # Light gray background

#         # Set global styles for labels
#         self.style.configure("TLabel", foreground="black", font=("Arial", 11))  # Black text

#         # Define styles for specific labels
#         self.style.configure("Title.TLabel", foreground="#4285F4", font=("Arial", 14, "bold"))  # Blue header
#         self.style.configure("Welcome.TLabel", foreground="black", font=("Arial", 14, "bold"))

#         # Define a style for LabelFrame (REMOVE BACKGROUND HERE)
#         self.style.configure("TLabelFrame", foreground="black", borderwidth=2, relief="solid")
#         self.style.configure("TLabelFrame.Label", foreground="#4285F4", font=("Arial", 12, "bold"))
        
#         # Define styles for buttons
#         self.style.configure("TButton", font=("Arial", 12, "bold"), padding=5, relief="flat", background="#1E90FF", foreground="white")  # Bright blue button

#         self.style.theme_use("clam")

#         # Define styles correctly
#         self.style.configure("Custom.TLabelframe", borderwidth=2, relief="solid")  # Removed background here
#         self.style.configure("Custom.TLabelframe.Label", foreground="#4285F4", font=("Arial", 12, "bold"))

#         # Initialize client data
#         self.client_data = {}

#         self.frames = {}
#         self.container = tk.Frame(self) #create container frame.
#         self.container.pack(side="top", fill="both", expand=True)
#         self.container.grid_rowconfigure(0, weight=1)
#         self.container.grid_columnconfigure(0, weight=1)

#             # Assuming you have a container to hold frames
#         for F in (EcesisLoginScreen,EntryScreen,ProfileScreen,PortalInstructionScreen):
#             print(f"value in loop : {F}")
#             page_name = F.__name__  # Getting the class name as the page name
#             frame = F(parent=self.container, controller=self)  # Creating the frame
#             self.frames[page_name] = frame  # Store the frame in a dictionary for easy access
#             frame.grid(row=0, column=0, sticky="nsew")  # Place the frame using grid layout
#         arg1="auto"
#         arg1, arg2, arg3 = params_check()
#         test = user_data.load_login_data()
        
#         if arg1 == "SmartEntry":
#             self.show_frame("EntryScreen")
#         elif arg1 == "PortalLogin":
#             self.show_frame("PortalInstructionScreen")
#         elif test.get("logged_in"):
#             self.show_frame("EcesisLoginScreen")
#         else:
#             self.show_frame("EcesisLoginScreen")
        

#     def show_frame(self, page_name):
#         """Bring the requested screen to the front."""
#         frame = self.frames[page_name]
#         print(f"Switching to frame: {page_name}")
#         frame.tkraise()


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