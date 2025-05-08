import tkinter as tk
from tkinter import ttk

class SettingsScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = ttk.Label(self, text="Settings Screen", font=("Arial", 18))
        label.pack(pady=20)

        btn = ttk.Button(self, text="Back to Home", command=lambda: controller.show_frame("EcesisLoginScreen"))
        btn.pack(pady=10)
