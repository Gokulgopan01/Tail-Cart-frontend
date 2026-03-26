import tkinter as tk
from tkinter import ttk
from integrations.hybrid_bpo_api import HybridBPOApi
from utils.vpn_connection import vpn_checking
import sys
import threading
from urllib.parse import urlparse, parse_qs
from utils.helper import params_check
from screens.loaded_screen import LoadedScreen
from utils.user_data import logout
class ProfileScreen(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Profile Label
        profile_label = tk.Label(self, text="Profile Screen", font=("Arial", 16))
        profile_label.pack(pady=10)

        # Logout Button
        logout_button = tk.Button(self, text="Logout", command=self.logout)
        logout_button.pack(pady=10)

    def logout(self):
        # Logic for logout
        logout()
        self.controller.show_frame("EcesisLoginScreen")