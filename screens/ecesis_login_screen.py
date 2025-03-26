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

from screens.portal_login_screen import PortalLoginScreen
import app

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

    def __init__(self,parent, controller):
        super().__init__(parent)
        self.controller = controller
        # Load Image

        # Button to go to another screen
        btn = ttk.Button(self, text="Go to Settings", command=lambda: controller.show_frame("SettingsScreen"))
        # btn = ttk.Button(self, text="Go to Settings", command=self.launch_browser)
        btn.pack(pady=10)



        # ttk.Button(self, text="MLS_Login",command=lambda:controller.show_frame("MlsScreen")).pack(pady=10)



        """Create a login UI with a dark blue, yellow, and white color scheme."""
        self.login_frame = tk.Frame(self, bg="#F0F0F0")  # Light gray background
        self.login_frame.pack(fill="both", expand=True)


        # Now create the LabelFrame with the correct style
        self.input_frame = ttk.LabelFrame(self.login_frame, padding=10, style="Custom.TLabelframe")
        self.input_frame.pack(pady=10, padx=20, ipadx=10, fill="x")
        # Initialize client data
        self.client_data = {}
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

        # Bind Enter key to focus on the password field when Enter is pressed
        self.email_entry.bind("<Return>", lambda event: self.password_entry.focus_set())

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
        # Bind Enter key to password entry (triggers login when pressed)
        self.password_entry.bind("<Return>", self.login)
        # Login Button
        self.sign_in_btn = tk.Button(self.login_frame, text="Login", font=("Arial", 14, "bold"),
                                      fg="white", bg="#1E90FF", activebackground="#1E90FF", bd=0,
                                      relief="flat", height=2, width=20, command=self.login)
        self.sign_in_btn.pack(pady=30, ipadx=20)
        # Bind Enter key to login function
        self.bind("<Return>", lambda event: self.login())

        # Center the elements
        self.login_frame.pack_propagate(False)

        # Bind focus events for placeholder behavior
        self.email_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(self.email_entry, "Enter your email"))
        self.email_entry.bind("<FocusOut>", lambda event: self.restore_placeholder(self.email_entry, "Enter your email"))

        self.password_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(self.password_entry, "Enter your password", hide_text=True))
        self.password_entry.bind("<FocusOut>", lambda event: self.restore_placeholder(self.password_entry, "Enter your password", hide_text=True))

        # Set initial placeholder text AFTER binding events
        self.email_var.set("Enter your email")
        self.password_var.set("Enter your password")


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
    

    def login(self, event=None):  # Accept event to handle Enter key press
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
                        self.after(0, lambda: self.show_client_login(username))
                    else:
                        self.after(0, lambda: messagebox.showerror("Error", "Invalid credentials"))
                else:
                    self.after(0, lambda: messagebox.showerror("Error", "Invalid email or password"))
            except requests.exceptions.RequestException as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Request failed: {e}"))

        threading.Thread(target=login_request, daemon=True).start()


    def forgot_password(self):
        messagebox.showinfo("Forgot Password", "Redirecting to password recovery page.")

    def show_welcome_message(self, username):
        """Displays a welcome message after successful login."""
        messagebox.showinfo("Success", f"Welcome, {username}!")

    def show_client_login(self, username):
        # """Shows the client selection UI after successful login."""
        # if hasattr(self, "login_frame"):
        #     self.login_frame.destroy()

        # If the login_frame exists, hide it instead of destroying it
        if hasattr(self, "login_frame"):
            self.login_frame.pack_forget()  # Hide the login frame
        # #  Initialize labels
        self.username_label = ttk.Label(self, text="Username: ")
        self.password_label = ttk.Label(self, text="Password: ")
        self.session_label = ttk.Label(self, text="Session: ")
        self.portal_url_label = ttk.Label(self, text="Portal URL: ")
        self.proxy_label=ttk.Label(self, text="Proxy: ")
      

        # Set background color
        self.configure(bg="#F2F2F2")  # Light Gray Background
        

            # **Top Frame for Logout Button**
        self.top_frame = tk.Frame(self, bg="#F2F2F2")
        self.top_frame.pack(fill="x", side="top", pady=10, padx=10)  # Attach to top with padding

        # **Logout Button (Top-Right Corner)**
        self.logout_button_top = tk.Button(self.top_frame, text="Logout", command=self.logout,
                                        font=("Arial", 10, "bold"), fg="white", bg="#FF0000",
                                        bd=0, relief="flat", height=1, width=10)
        self.logout_button_top.pack(side="right", anchor="ne", padx=10, pady=5)

        # Main client frame
        self.client_frame = tk.Frame(self, bg="#F2F2F2")
        self.client_frame.pack(fill="both", expand=True)

        # Inner Frame (White Box)
        self.inner_frame = tk.Frame(self.client_frame, bg="white", bd=2, relief="solid")
        self.inner_frame.pack(pady=50, padx=50, expand=True)

        # Welcome Message
        ttk.Label(self.inner_frame, text=f"Welcome, {username}!", font=("Arial", 14, "bold"), background="white").pack(pady=(10, 15))
        ttk.Label(self.inner_frame, text="Select Client Details", font=("Arial", 12, "bold"), background="white").pack(pady=(0, 20))

        # Dropdown Styling
        dropdown_width = 30

        # Main Client Dropdown
        self.main_client_var = tk.StringVar()
        self.main_client_dropdown = self.create_combobox(self.inner_frame, self.main_client_var, "Select Main Client", self.on_main_client_select)
        self.main_client_dropdown.pack(pady=5, padx=20, fill="x")
        self.main_client_dropdown.bind("<Return>", lambda event: self.sub_client_dropdown.focus_set())  # Move to Sub Client


        # Sub Client Dropdown
        self.sub_client_var = tk.StringVar()
        self.sub_client_dropdown = self.create_combobox(self.inner_frame, self.sub_client_var, "Select Sub Client", self.on_sub_client_select)
        self.sub_client_dropdown.pack(pady=5, padx=20, fill="x")
        self.sub_client_dropdown.bind("<Return>", lambda event: self.portal_dropdown.focus_set())  # Move to Portal


        # Portal Dropdown
        self.portal_var = tk.StringVar()
        self.portal_dropdown = self.create_combobox(self.inner_frame, self.portal_var, "Select Portal", self.on_portal_select)
        self.portal_dropdown.pack(pady=5, padx=20, fill="x")
        self.portal_dropdown.bind("<Return>", lambda event: self.account_dropdown.focus_set())  # Move to Account
    # Move to the Login Button


        # Account Dropdown
        self.account_var = tk.StringVar()
        self.account_dropdown = self.create_combobox(self.inner_frame, self.account_var, "Select Account", self.on_account_select)
        self.account_dropdown.pack(pady=5, padx=20, fill="x")
        self.account_dropdown.bind("<Return>", lambda event: self.confirm_selection())  # Move to the Login Button

        # Login Button
        self.login_button = tk.Button(self.inner_frame, text="Login to Portal", command=self.confirm_selection,
                                      font=("Arial", 12, "bold"), fg="white", bg="#007BFF", bd=0, relief="flat", height=2, width=20)
        self.login_button.pack(pady=10)

        threading.Thread(target=self.load_main_clients, daemon=True).start()

    def create_combobox(self, parent, var, placeholder, callback):
        """Create a searchable dropdown with a placeholder."""
        cb = ttk.Combobox(parent, textvariable=var, width=30, state="readonly")
        cb.set(placeholder)
        cb.bind("<<ComboboxSelected>>", callback)
        return cb

    # def logout(self):
    #     """Logs out the user, resets UI, and clears login fields."""
    #     confirm = messagebox.askyesno("Logout", "Are you sure you want to log out?")
    #     if confirm:
    #         # Hide the client frame
    #         if hasattr(self, "client_frame"):
    #             self.client_frame.pack_forget()

    #         # Unhide the login frame
    #         if hasattr(self, "login_frame"):
    #             self.login_frame.pack(fill="both", expand=True)

    #             # **Restore placeholders for email and password fields**
    #         if hasattr(self, "email_entry"):
    #             self.email_entry.delete(0, tk.END)  # Clear the field
    #             self.email_entry.insert(0, "Enter your email")  # Restore placeholder
    #         if hasattr(self, "password_entry"):
    #             self.password_entry.delete(0, tk.END)  # Clear the field
    #             self.password_entry.insert(0, "Enter your password")  # Restore placeholder
    #             #self.password_entry.config(show="")  # Ensure it appears as placeholder text

    #         # **Hide the logout button on the login screen**
    #         if hasattr(self, "logout_button_top"):
    #             self.logout_button_top.pack_forget()  # Hide the logout button

    #         # Set focus to login button after logout
    #         self.after(100, self.login_button.focus_set)
    #         # Switch to the login screen
    #         self.controller.show_frame("EcesisLoginScreen")

    def logout(self):
        """Logs out the user, resets UI, and clears login fields."""
        confirm = messagebox.askyesno("Logout", "Are you sure you want to log out?")
        if confirm:
            # Hide the client frame
            if hasattr(self, "client_frame"):
                self.client_frame.pack_forget()

            # Unhide the login frame
            if hasattr(self, "login_frame"):
                self.login_frame.pack(fill="both", expand=True)
            
            # Restore placeholders for email and password fields
            if hasattr(self, "email_entry"):
                self.email_entry.delete(0, tk.END)  # Clear the field
                self.email_entry.insert(0, "Enter your email")  # Restore placeholder
            
            if hasattr(self, "password_entry"):
                self.password_entry.delete(0, tk.END)  # Clear the field
                self.password_entry.insert(0, "Enter your password")  # Restore placeholder
            
            # Hide the logout button if present
            if hasattr(self, "logout_button_top"):
                self.logout_button_top.pack_forget()

            # Ensure the login frame is brought to the front
            self.controller.show_frame("EcesisLoginScreen")
            
            # Delay focus setting to ensure UI update
            if hasattr(self, "login_button"):
                self.after(200, self.login_button.focus_set)  # Use root.after to avoid timing issues


    def clear_screen(self):
        """Clears the current UI."""
        for widget in self.winfo_children():
            widget.destroy()

    def load_main_clients(self):
        """Fetch and populate main clients."""
        response = self.fetch_data(MAIN_CLIENTS_API)
        if response:
            self.client_data["main_clients"] = response
            self.main_client_dropdown["values"] = [c["client_name"] for c in self.client_data["main_clients"]]

    def on_main_client_select(self, event):
        """Handle main client selection and fetch sub-clients."""
        selected_client = next((c for c in self.client_data["main_clients"] if c["client_name"] == self.main_client_var.get()), None)
        if selected_client:
            client_id = selected_client["id"]
            threading.Thread(target=self.load_sub_clients, args=(client_id,), daemon=True).start()

    def load_sub_clients(self, client_id):
        """Fetch and populate sub-clients."""
        #self.client_data["sub_clients"] = self.account_fetch_data(SUB_CLIENTS_API,{"mainClientId":client_id})
        response = self.account_fetch_data(SUB_CLIENTS_API,{"mainClientId":client_id})
        print(response)
        if response and response.get("status_code") == 200 and response.get("content") and response.get("content").get("data"):
            sub_clients_data = response["content"]["data"]
            self.client_data["sub_clients"] = response #store the entire response, not just the data.
            self.sub_client_dropdown["values"] = [sc["client_name"] for sc in sub_clients_data]
        else:
            # Handle cases where the API response is not in the expected format
            messagebox.showerror("Error", "Failed to load sub-clients or unexpected API response.")
    def on_sub_client_select(self, event):
        """Handle sub-client selection and store `sub_client_id` for later use."""
        sub_clients_data = self.client_data["sub_clients"]["content"]["data"]
        selected_sub_client = next((sc for sc in sub_clients_data if sc["client_name"] == self.sub_client_var.get()), None)

        if selected_sub_client:
            self.selected_sub_client_id = selected_sub_client["sub_client_id"]
            threading.Thread(target=self.load_portals, args=(self.selected_sub_client_id,), daemon=True).start()

    def load_portals(self, sub_client_id):
        """Fetch and populate portals."""
        response = self.account_fetch_data(PORTALS_API, {"client_id": sub_client_id})
        if response:
            self.client_data["portals"] = response["content"]["data"]
            self.portal_dropdown["values"] = [p["portal_name"] for p in self.client_data["portals"]]

    def on_portal_select(self, event):
        """Handle portal selection and fetch accounts."""
        selected_portal = next((p for p in self.client_data["portals"] if p["portal_name"] == self.portal_var.get()), None)
        if selected_portal:
            self.selected_portal_id = selected_portal["portal_id"]
            self.selected_portal_url = selected_portal["portal_url"]
            threading.Thread(target=self.load_accounts, args=(self.selected_sub_client_id, self.selected_portal_id), daemon=True).start()

    def load_accounts(self, sub_client_id, portal_id):
        """Fetch and populate accounts."""
        response = self.account_fetch_data(ACCOUNT_API, {"client_id": sub_client_id, "portal_id": portal_id})
        if response:
            self.accounts = response["content"]["data"]
            self.account_dropdown["values"] = [str(acc["account_id"]) for acc in self.accounts]

    def on_account_select(self, event):
        """Handle account selection and display details."""
        selected_account = next((acc for acc in self.accounts if str(acc["account_id"]) == self.account_var.get()), None)
        if selected_account:
            self.load_selected_account_info(selected_account)

    def load_selected_account_info(self, account):
        """Display selected account details."""
        self.username_label.config(text=f"Username: {account['username']}")
        self.password_label.config(text=f"Password: {account['password']}")
        self.session_label.config(text=f"Session: {account['session']}")
        self.portal_url_label.config(text=f"Portal URL: {self.selected_portal_url}")
        self.proxy_label.config(text=f"Proxy: {account['proxy']}")

    
    def confirm_selection(self):
        """Confirm selection and trigger login."""
        if self.main_client_var.get() and self.sub_client_var.get() and self.portal_var.get() and self.account_var.get():
            selected_account = next((acc for acc in self.accounts if acc["account_id"] == int(self.account_var.get())), None)
            if selected_account:
                self.login_to_portal(selected_account)
            else:
                messagebox.showerror("Error", "Selected account not found.")
        else:
            messagebox.showwarning("Incomplete", "Please select all details to proceed.")

    def login_to_portal(self, selected_account):
        """Login to the portal with the selected account details."""
        portal = self.portal_var.get()
        if portal:
            portal_login = PortalLoginScreen.portals(selected_account["username"], selected_account["password"], self.selected_portal_url, portal,selected_account["proxy"])  # Create PortalLogin instance using portals
            threading.Thread(
                target=portal_login.login_to_portal,  # Correct thread target
                args=(selected_account["username"], selected_account["password"], self.selected_portal_url, portal,selected_account["proxy"]),
                daemon=True
            ).start()
        else:
            messagebox.showerror("Error", "Portal login function not found.")

    def fetch_data(self, endpoint, params=None):
        """Fetch data from API and return JSON response."""
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            print(f"API Response from {endpoint}: {data}")
            if isinstance(data, dict) and data.get("status_code") == 200:
                return data.get("content", {}).get("data", [])
            messagebox.showerror("Error", f"Unexpected API response structure: {data}")
            return None
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to fetch data: {e}")
            return None

    def account_fetch_data(self, endpoint, params=None):
        """Fetch data from API with proper error handling."""
        try:
            response = requests.get(endpoint, params=params, timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                messagebox.showerror("Error", f"Failed to fetch data: {response.status_code}")
                return {"status_code": response.status_code, "content": {"data": []}}
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Request failed: {e}")
            return {"status_code": 500, "content": {"data": []}}

    


