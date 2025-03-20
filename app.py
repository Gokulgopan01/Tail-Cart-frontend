import tkinter as tk
from tkinter import ttk
from screens.ecesis_login_screen import EcesisLoginScreen
from screens.settings_screen import SettingsScreen

class Application(tk.Tk):
    def __init__(self,root):
        super().__init__()
        self.root = root
        self.root.title("ECESIS - Login")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        # Bring the window to the front
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(1000, lambda: self.root.attributes('-topmost', False))

        # Apply background color
        self.root.configure(bg="#F0F0F0")  # Light gray background

        """Create a login UI with a dark blue, yellow, and white color scheme."""
        self.login_frame = tk.Frame(self.root, bg="#F0F0F0")  # Light gray background
        self.login_frame.pack(fill="both", expand=True)


        # Now create the LabelFrame with the correct style
        self.input_frame = ttk.LabelFrame(self.login_frame, padding=10, style="Custom.TLabelframe")
        self.input_frame.pack(pady=10, padx=20, ipadx=10, fill="x")

        # Define styles
        self.style = ttk.Style()

        # Set background color for frames
        self.style.configure("TFrame",  background="#FFFFFF")  # Light gray background

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

        for F in (EcesisLoginScreen, SettingsScreen):
            page_name = F.__name__
            frame = F(root=self,parent=self, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("EcesisLoginScreen")

    def show_frame(self, page_name):
        """Bring the requested screen to the front."""
        frame = self.frames[page_name]
        frame.tkraise()
