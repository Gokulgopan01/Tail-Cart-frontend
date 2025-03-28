import sys
import tkinter as tk
from tkinter import Image, ttk
from screens.ecesis_login_screen import EcesisLoginScreen
from screens.mls_screen import MlsScreen
from screens.settings_screen import SettingsScreen
from urllib.parse import urlparse, parse_qs
from utils.helper import params_check
from utils.file_util import resource_path
from PIL import Image, ImageDraw, ImageTk

class Application(tk.Tk):
    def __init__(self): #root passed but not used.
        super().__init__() #super init.
        self.title("ECESIS - Login")
        self.geometry("800x650") #corrected geometry.
        self.resizable(True, True)
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
        self.configure(bg="#F0F0F0")  # Light gray background

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

        for F in (EcesisLoginScreen, SettingsScreen, MlsScreen):
            print(f"value in loop : {F}")
            page_name = F.__name__
            frame = F(parent=self.container, controller=self) #correct parent pass.
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")    

        # login screen  
        arg1,arg2= params_check()    
        
        if arg1:
            if 'mlsdownloader' in arg1 :
                print("mls creen called")
                self.show_frame("MlsScreen")
            elif 'SmartEntry' in arg1 :
                self.show_frame("MlsScreen") #call the class created for entry
            else:     
                self.show_frame("MlsScreen") # call the class created for portal login
        else:  
            self.show_frame("EcesisLoginScreen")


    def show_frame(self, page_name):
        """Bring the requested screen to the front."""
        frame = self.frames[page_name]
        frame.tkraise()
