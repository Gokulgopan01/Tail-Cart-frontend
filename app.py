import sys
import tkinter as tk
from tkinter import Image, ttk
from screens.ecesis_login_screen import EcesisLoginScreen
from screens.entry_screen import EntryScreen
from screens.mls_screen import MlsScreen
from screens.portal_login_screen import PortalLoginScreen
from screens.settings_screen import SettingsScreen
from urllib.parse import urlparse, parse_qs
from utils.helper import center_window, params_check
from utils.file_util import resource_path
from PIL import Image, ImageDraw, ImageTk
from utils import user_data
from screens.profile_screen import ProfileScreen
class Application(tk.Tk):
    def __init__(self): #root passed but not used.
        super().__init__() #super init.
        self.title("ECESIS - Login")
        self.geometry("800x650") #corrected geometry.
        self.resizable(True, True)
        # Center the window
        center_window(self, 800, 650)
        img_path = resource_path("logo.jpg")
        image = Image.open(img_path)
        image = image.resize((100, 100))  # Resize if needed
        self.logo = ImageTk.PhotoImage(image)
        # Set the window icon
        self.iconphoto(False, self.logo)  # False ensures the icon applies to all windows
        # Bring the window to the front
        self.lift()
        self.attributes('-topmost', True)
        self.after(1000, lambda: self.attributes('-topmost', False))

        # Apply background color
        self.configure(bg="#FFFFFF")  # White background

        # Define styles
        self.style = ttk.Style()

        # Set background color for frames
        self.style.configure("TFrame", background="#FFFFFF")  # Light gray background

        # Set global styles for labels
        self.style.configure("TLabel", foreground="black", font=("Arial", 11))  # Black text

        # Define styles for specific labels
        self.style.configure("Title.TLabel", foreground="#4285F4", font=("Arial", 14, "bold"))  # Blue header
        self.style.configure("Welcome.TLabel", foreground="black", font=("Arial", 14, "bold"))

        # Define a style for LabelFrame (REMOVE BACKGROUND HERE)
        self.style.configure("TLabelFrame", foreground="black", borderwidth=2, relief="solid")
        self.style.configure("TLabelFrame.Label", foreground="#4285F4", font=("Arial", 12, "bold"))
        
        # Define styles for buttons
        self.style.configure("TButton", font=("Arial", 12, "bold"), padding=5, relief="flat", background="#1E90FF", foreground="white")  # Bright blue button

        self.style.theme_use("clam")

        # Define styles correctly
        self.style.configure("Custom.TLabelframe", borderwidth=2, relief="solid")  # Removed background here
        self.style.configure("Custom.TLabelframe.Label", foreground="#4285F4", font=("Arial", 12, "bold"))

        # Initialize client data
        self.client_data = {}

        self.frames = {}
        self.container = tk.Frame(self) #create container frame.
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

            # Assuming you have a container to hold frames
        for F in (EcesisLoginScreen, SettingsScreen,EntryScreen,ProfileScreen):
            print(f"value in loop : {F}")
            page_name = F.__name__  # Getting the class name as the page name
            frame = F(parent=self.container, controller=self)  # Creating the frame
            self.frames[page_name] = frame  # Store the frame in a dictionary for easy access
            frame.grid(row=0, column=0, sticky="nsew")  # Place the frame using grid layout

        # Login screen logic
        arg1, arg2 = params_check()  # Assuming params_check() parses the arguments
        #arg1 = "SmartEntry"  # You set arg1 manually here for testing

        # Check if arg1 contains specific parameters and show the appropriate screen
        if arg1:
            if 'SmartEntry' in arg1:
                print("Entry Screen called")
                self.show_frame("EntryScreen")  # Show the Entry screen
        else:
             # check if logged In :
            test = user_data.load_login_data()
            print("login data",test['logged_in'])
            if test['logged_in']:
                self.show_frame("ProfileScreen")
            else:
                self.show_frame("EcesisLoginScreen")


        # for F in (EcesisLoginScreen, SettingsScreen):
        #     print(f"value in loop : {F}")
        #     page_name = F.__name__
        #     frame = F(parent=self.container, controller=self) #correct parent pass.
        #     self.frames[page_name] = frame
        #     frame.grid(row=0, column=0, sticky="nsew")    

        # # login screen  
       
        # self.show_frame("EcesisLoginScreen")


    def show_frame(self, page_name):
        """Bring the requested screen to the front."""
        frame = self.frames[page_name]
        frame.tkraise()