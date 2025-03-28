import tkinter as tk
from tkinter import ttk
from integrations.hybrid_bpo_api import HybridBPOApi
from integrations.mls_automation.gamls import Gamls
from integrations.mls_automation.fmls import Fmls
from utils.pic_pdf_downloads.vpn_connection import vpn_checking
import sys
import threading


import sys
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import tkinter as tk
from tkinter import ttk

class LoadedScreen(tk.Frame):
    def __init__(self, parent, controller, title_text, status_text):
        super().__init__(parent)
        self.controller = controller

         # Frame Background Color
        self.configure(bg="#F2F2F2")

        # Title Label (Dynamic)
        self.title_label = ttk.Label(self, text=title_text, font=("Arial", 20, "bold"), background="#F2F2F2")
        self.title_label.pack(pady=15)

        # Progress Bar with Modern Look
        self.progress = ttk.Progressbar(self, orient="horizontal", length=300, mode="indeterminate", style="TProgressbar")
        self.progress.pack(pady=10)
        self.progress.start()

        # Status Label (Dynamic)
        self.status_label = ttk.Label(self, text=status_text, font=("Arial", 14, "italic"), foreground="gray", background="#F2F2F2")
        self.status_label.pack(pady=5)

        # Exit Button with Hover Effect
        self.exit_button = tk.Button(self, text="Close", command=self.on_exit,
                                     font=("Arial", 12, "bold"), fg="white", bg="#FF5555",
                                     bd=0, relief="flat", height=1, width=12)
        self.exit_button.pack(pady=15)

        # Add hover effect for the button
        self.exit_button.bind("<Enter>", self.on_hover_in)
        self.exit_button.bind("<Leave>", self.on_hover_out)

        # Packing the frame to display it
        self.pack(fill="both", expand=True)


    def update_status(self, title=None, status=None):
        """Update title and status dynamically from another script."""
        if title:
            self.title_label.config(text=title)
        if status:
            self.status_label.config(text=status)
        self.update_idletasks()  # Force UI update

    def on_exit(self):
        """Exit confirmation dialog before closing the app."""
        result = messagebox.askquestion("Exit", "Are you sure you want to exit?", icon="warning")
        if result == 'yes':
            self.controller.quit()

    def on_hover_in(self, event):
        """Change button color when mouse enters."""
        self.exit_button.config(bg="#FF3333")

    def on_hover_out(self, event):
        """Revert button color when mouse leaves."""
        self.exit_button.config(bg="#FF5555")