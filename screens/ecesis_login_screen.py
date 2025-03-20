import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from utils.file_util import resource_path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

import os
import tkinter as tk
from tkinter import DISABLED, NORMAL, ttk, messagebox
import threading
import requests
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageTk

# Load variables from .env file
load_dotenv()

# Retrieve API URLs from environment variables
BASE_URL = os.getenv("BASE_URL")
LOGIN_API = os.getenv("LOGIN_API")

# Construct API endpoints dynamically
MAIN_CLIENTS_API = f"{BASE_URL}/getMainClients"
SUB_CLIENTS_API = f"{BASE_URL}/getSubclientByMainClient"
PORTALS_API = f"{BASE_URL}/getClientPortals"
ACCOUNT_API = f"{BASE_URL}/getAccountInfo"

#Print API URLs (Remove in Production)
print(f"Main Clients API: {MAIN_CLIENTS_API}")
print(f"Login API: {LOGIN_API}")


class EcesisLoginScreen(tk.Frame):

    # def launch_browser(self):

    #         # Configure Selenium WebDriver
    #         chrome_options = Options()
    #         chrome_options.add_argument("--start-maximized")
    #         # service = Service("path/to/chromedriver")  # Replace with the actual path to chromedriver
    #         driver = webdriver.Chrome( options=chrome_options)

    #         # Open a website
    #         driver.get("https://www.example.com")
    #         time.sleep(1000)
    #         # btn.pack(pady=10)
    
    def __init__(self, root,parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.root = root #store root.

        # Load Image
        img_path = resource_path("logo.jpg")
        image = Image.open(img_path)
        image = image.resize((100, 100))  # Resize if needed
        self.logo = ImageTk.PhotoImage(image)

        # Display Image
        label = tk.Label(self, image=self.logo)
        label.pack(pady=20)

        # Button to go to another screen
        btn = ttk.Button(self, text="Go to Settings", command=lambda: controller.show_frame("SettingsScreen"))
        # btn = ttk.Button(self, text="Go to Settings", command=self.launch_browser)
        btn.pack(pady=10)

        self.create_login_frame()
    def create_login_frame(self):
        ttk.Label(self.login_frame, text="ECESIS", font=("Arial", 14, "bold"), background="#F0F0F0").pack(pady=10)
        ttk.Label(self.login_frame, text="HYBRID CLIENT LOGIN", font=("Arial", 16, "bold"), background="#F0F0F0").pack(pady=20)
        ttk.Label(self.login_frame, text="Welcome back! Please login to your account to continue", font=("Arial", 10), background="#F0F0F0").pack(pady=5)

        # Use a Frame instead of ttk.LabelFrame
        self.input_frame = tk.Frame(self.login_frame, bg="#F0F0F0", bd=2, relief="solid", padx=10, pady=10)
        self.input_frame.pack(pady=10, padx=20, fill="x")

        # Email Entry (No Label)
        self.email_var = tk.StringVar()
        self.email_entry = ttk.Entry(self.input_frame, font=("Arial", 11), textvariable=self.email_var, foreground="gray", background="white")
        self.email_entry.pack(pady=10, padx=10, fill="x", ipady=5)
        self.email_var.set("Enter your email")

        # Password Entry (No Label)
        password_frame = tk.Frame(self.input_frame, bd=1, relief="solid", bg="white")
        password_frame.pack(pady=10, padx=10, fill="x")

        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(password_frame, font=("Arial", 11), textvariable=self.password_var, foreground="gray", background="white", relief="flat", bd=0)
        self.password_entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(5, 0))
        self.password_var.set("Enter your password")

        # Toggle Button Inside the Password Box
        self.show_password_btn = tk.Button(password_frame, text="👁", font=("Arial", 10), relief="flat", bd=0, cursor="hand2", bg="white", command=self.toggle_password)
        self.show_password_btn.pack(side="right", padx=(0, 5))

        # Forgot Password
        forgot_password_frame = tk.Frame(self.login_frame, bg="#F0F0F0")
        forgot_password_frame.pack(pady=15)
        tk.Button(forgot_password_frame, text="Forgot Password", font=("Arial", 9, "bold"), fg="white",
                  bg="#1E90FF", relief="flat", cursor="hand2", command=self.forgot_password).pack(pady=5)

        # Login Button
        self.sign_in_btn = tk.Button(self.login_frame, text="Login", font=("Arial", 14, "bold"),
                                      fg="white", bg="#1E90FF", activebackground="#1E90FF", bd=0,
                                      relief="flat", height=2, width=20, command=self.login)
        self.sign_in_btn.pack(pady=30, ipadx=20)

        # Center the elements
        self.login_frame.pack_propagate(False)

        # Bind focus events for placeholder behavior
        self.email_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(self.email_entry, "Enter your email"))
        self.email_entry.bind("<FocusOut>", lambda event: self.restore_placeholder(self.email_entry, "Enter your email"))

        self.password_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(self.password_entry, "Enter your password", hide_text=True))
        self.password_entry.bind("<FocusOut>", lambda event: self.restore_placeholder(self.password_entry, "Enter your password", hide_text=True))



    def clear_placeholder(self, entry, placeholder, hide_text=False):
        """Clears the placeholder text when the user clicks inside the field."""
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(foreground="black")
            if hide_text:
                entry.config(show="*")

    def restore_placeholder(self, entry, placeholder, hide_text=False):
        """Restores the placeholder if the field is left empty."""
        if entry.get() == "":
            entry.insert(0, placeholder)
            entry.config(foreground="gray")
            if hide_text:
                entry.config(show="")

    def toggle_password(self):
        """Toggle password visibility."""
        if self.password_entry.cget('show') == '*':
            self.password_entry.config(show='')
            self.show_password_btn.config(text='🙈')  # Change text to hide password
        else:
            self.password_entry.config(show='*')
            self.show_password_btn.config(text='👁')  # Change text to show password
    

    def login(self):
        """Handles user login via API."""
        email = self.email_entry.get()
        password = self.password_entry.get()
        payload = {"email": email, "password": password}

        def login_request():
            try:
                response = requests.post(LOGIN_API, json=payload, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status_code") == 200 and data.get("content", {}).get("data", {}).get("success"):
                        username = data["content"]["data"]["username"]
                        #self.root.after(0, lambda: self.show_welcome_message(username))
                        self.root.after(0, lambda: self.show_client_login(username))
                    else:
                        self.root.after(0, lambda: messagebox.showerror("Error", "Invalid credentials"))
                else:
                    self.root.after(0, lambda: messagebox.showerror("Error", "Invalid email or password"))
            except requests.exceptions.RequestException as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Request failed: {e}"))

        threading.Thread(target=login_request, daemon=True).start()

    def forgot_password(self):
        messagebox.showinfo("Forgot Password", "Redirecting to password recovery page.")

    def show_welcome_message(self, username):
        """Displays a welcome message after successful login."""
        messagebox.showinfo("Success", f"Welcome, {username}!")
    


