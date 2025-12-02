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

# class LoadedScreen(tk.Frame):
#     def __init__(self, parent, controller, title_text, status_text):
#         super().__init__(parent)
#         self.controller = controller

#          # Frame Background Color
#         self.configure(bg="#FFFFFF")

#         self.inner_frame = tk.Frame(self, bg="white")
#         self.inner_frame.pack(padx=50, expand=True) #created to center the frame

#         # Title Label (Dynamic)
#         self.title_label = ttk.Label(self.inner_frame, text=title_text, font=("sans-serif", 17), background="#FFFFFF")
#         self.title_label.pack(pady=15)

#         # Progress Bar with Modern Look       
#         self.progress = ttk.Progressbar(self.inner_frame, orient="horizontal", length=300, mode="indeterminate", style="TProgressbar")
#         self.progress.pack(pady=10)
#         self.progress.start()

#         # Status Label (Dynamic)
#         self.status_label = ttk.Label(self.inner_frame, text=status_text, font=("sans-serif", 14, "italic"), foreground="black", background="#FFFFFF")
#         self.status_label.pack(pady=5)

#         # Exit Button with Hover Effect
#         self.exit_button = tk.Button(self.inner_frame, text="Close", command=self.on_exit,
#                                      font=("sans-serif", 12, "bold"), fg="white", bg="#1877F2",
#                                      bd=0, relief="flat", height=1, width=12)
#         self.exit_button.pack(pady=15)

#         # Add hover effect for the button
#         self.exit_button.bind("<Enter>", self.on_hover_in)
#         self.exit_button.bind("<Leave>", self.on_hover_out)

#         # Packing the frame to display it
#         self.pack(fill="both", expand=True)


#     def update_status(self, title=None, status=None,loading=None):
#         """Update title and status dynamically from another script."""
#         if title:
#             self.title_label.config(text=title)
#         if status:
#             self.status_label.config(text=status)
#         if loading:
#             self.progress.destroy()          
#         self.update_idletasks()  # Force UI update

#     def on_exit(self):
#         """Exit confirmation dialog before closing the app."""
#         result = messagebox.askquestion("Exit", "Are you sure you want to exit?", icon="warning")
#         if result == 'yes':
#             self.controller.quit()

#     def on_hover_in(self, event):
#         """Change button color when mouse enters."""
#         self.exit_button.config(bg="#1565D8")

#     def on_hover_out(self, event):
#         """Revert button color when mouse leaves."""
#         self.exit_button.config(bg="#1877F2")


class LoadedScreen(tk.Frame):
    def __init__(self, parent, controller, title_text, status_text, on_exit_callback=None):
        super().__init__(parent)
        self.controller = controller
        self.on_exit_callback = on_exit_callback  # Callback to notify EntryScreen to exit

        self.configure(bg="#FFFFFF")

        self.inner_frame = tk.Frame(self, bg="white")
        self.inner_frame.pack(padx=50, pady=50, expand=True)  # Center the frame

        self.title_label = ttk.Label(
            self.inner_frame,
            text=title_text,
            font=("sans-serif", 17),
            background="#FFFFFF"
        )
        self.title_label.pack(pady=15)

        self.progress = ttk.Progressbar(
            self.inner_frame,
            orient="horizontal",
            length=300,
            mode="indeterminate",
            style="TProgressbar"
        )
        self.progress.pack(pady=10)
        self.progress.start()

        self.status_label = ttk.Label(
            self.inner_frame,
            text=status_text,
            font=("sans-serif", 14, "italic"),
            foreground="black",
            background="#FFFFFF"
        )
        self.status_label.pack(pady=5)

        self.exit_button = tk.Button(
            self.inner_frame,
            text="Close",
            font=("sans-serif", 12, "bold"),
            fg="white",
            bg="#1877F2",
            bd=0,
            relief="flat",
            height=1,
            width=12,
            command=self.on_exit
        )
        self.exit_button.pack(pady=15)

        self.exit_button.bind("<Enter>", lambda e: self.exit_button.config(bg="#1565D8"))
        self.exit_button.bind("<Leave>", lambda e: self.exit_button.config(bg="#1877F2"))

        self.pack(fill="both", expand=True)

    def update_status(self, title=None, status=None, loading=None):
        if title:
            self.title_label.config(text=title)
        if status:
            self.status_label.config(text=status)
        if loading:
            self.progress.destroy()
        self.update_idletasks()

    def on_exit(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            # Call the callback to notify EntryScreen to close
            if self.on_exit_callback:
                self.on_exit_callback()
