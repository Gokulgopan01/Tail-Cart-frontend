import tkinter as tk
from tkinter import ttk
from integrations.hybrid_bpo_api import HybridBPOApi

class HomeScreen(tk.Frame):
    def __init__(self, parent, controller):

        super().__init__(parent)
        self.controller = controller
        self.hybridIntegration = HybridBPOApi()

        ttk.Label(self, text="Login Screen", font=("Helvetica", 14)).pack(pady=10)

        ttk.Label(self, text="Username:").pack(pady=5)
        self.entry_username = ttk.Entry(self)
        self.entry_username.pack(pady=5)

        ttk.Label(self, text="Password:").pack(pady=5)
        self.entry_password = ttk.Entry(self, show="*")
        self.entry_password.pack(pady=5)

        ttk.Button(self, text="Login").pack(pady=10)

        # check if autologin version is correct

        version_check = self.check_if_version()

        if not version_check:

            self.download_new_version()

        else:

            self.check_if_already_loggedIn()



    def check_if_already_loggedIn():

        # check if the user is already logged in also, check if the user login expired by date
        1

    
    def check_if_version(self):

        try:
            self.hybridIntegration.check_application_version() 
        except Exception as e:
            print("e")
                 

    def download_new_version(self):
        try:
            1
        except Exception as e:
            print("e")

