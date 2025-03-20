import tkinter as tk
from tkinter import ttk
from utils import file_util
from PIL import Image, ImageTk

class LoginScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        img_path = file_util.resource_path("logo.jpg")
        image = Image.open(img_path)
        image = image.resize((100, 100))  # Resize if needed
        self.logo = ImageTk.PhotoImage(image)

        # Display Image
        label = tk.Label(self, image=self.logo)
        label.pack(pady=20)

        # ttk.Label(self, text="Login Screen", font=("Helvetica", 14)).pack(pady=10)

        # ttk.Label(self, text="Username:").pack(pady=5)
        # self.entry_username = ttk.Entry(self)
        # self.entry_username.pack(pady=5)

        # ttk.Label(self, text="Password:").pack(pady=5)
        # self.entry_password = ttk.Entry(self, show="*")
        # self.entry_password.pack(pady=5)

        # ttk.Button(self, text="Login").pack(pady=10)
        
