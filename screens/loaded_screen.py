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

        # Title Label (Dynamic)
        self.title_label = ttk.Label(self, text=title_text, font=("Arial", 18, "bold"))
        self.title_label.pack(pady=15)

        # Progress Bar
        self.progress = ttk.Progressbar(self, orient="horizontal", length=250, mode="indeterminate")
        self.progress.pack(pady=10)
        self.progress.start()

        # Status Label (Dynamic)
        self.status_label = ttk.Label(self, text=status_text, font=("Arial", 12, "italic"), foreground="gray")
        self.status_label.pack(pady=5)

        # Exit Button
        self.exit_button = tk.Button(self, text="Close", command=self.controller.quit,
                                     font=("Arial", 12, "bold"), fg="white", bg="#FF5555",
                                     bd=0, relief="flat", height=1, width=10)
        self.exit_button.pack(pady=15)

    def update_status(self, title=None, status=None):
        """Update title and status dynamically from another script."""
        if title:
            self.title_label.config(text=title)
        if status:
            self.status_label.config(text=status)
        self.update_idletasks()  # Force UI update
        