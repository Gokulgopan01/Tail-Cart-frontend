

import os
import tkinter as tk
from tkinter import DISABLED, NORMAL, ttk, messagebox
import threading
import requests
from portal.Proteck import PortalLogin  #Import the class from proteck.py
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Retrieve API URLs from environment variables
BASE_URL = os.getenv("BASE_URL")
LOGIN_API = os.getenv("LOGIN_API")

# Construct API endpoints dynamically
MAIN_CLIENTS_API = f"{BASE_URL}/getMainClients"
SUB_CLIENTS_API = f"{BASE_URL}/getSubClients"
PORTALS_API = f"{BASE_URL}/getClientPortals"
ACCOUNT_API = f"{BASE_URL}/getAccountInfo"

#Print API URLs (Remove in Production)
print(f"Main Clients API: {MAIN_CLIENTS_API}")
print(f"Login API: {LOGIN_API}")


class UserSelectionApp:
    def __init__(self, root, portal_login):
        self.root = root
        self.root.title("Client Login")
        self.root.geometry("500x500")
        #self.root.state("zoomed")  # Maximizes the window
        self.root.resizable(False, False)

        # --- Login Frame ---
        login_frame = ttk.Frame(root, padding=20)
        login_frame.pack(fill="both", expand=True)

        ttk.Label(login_frame, text="ECESIS", font=("Arial", 14, "bold")).pack(pady=10)
        ttk.Label(login_frame, text="HYBRID CLIENT LOGIN", font=("Arial", 16, "bold")).pack(pady=20)
        ttk.Label(login_frame, text="Welcome back! Please login to your account to continue", font=("Arial", 10)).pack(pady=5)
        # Frame with Border for Email and Password
        input_frame = ttk.LabelFrame(login_frame , padding=10)
        input_frame.pack(pady=10, padx=10, fill="x")

        # Email Entry
        ttk.Label(input_frame, text="Email Address:").pack(anchor="w", padx=5, pady=(5, 0))
        self.email_entry = ttk.Entry(input_frame, font=("Arial", 11))
        self.email_entry.pack(pady=5, padx=10, fill="x", ipady=5)
        self.email_entry.insert(0, "example@gmail.com")

        # Password Entry with Embedded Toggle Button
        ttk.Label(input_frame, text="Password:").pack(anchor="w", padx=5, pady=(5, 0))
        password_frame = tk.Frame(input_frame, bd=1, relief="solid")
        password_frame.pack(pady=5, padx=10, fill="x")

        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(password_frame, font=("Arial", 11), show="*", textvariable=self.password_var, relief="flat", bd=0)
        self.password_entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(5, 0))
        self.password_entry.insert(0, "password123")

        # Toggle Button Inside the Password Box
        self.show_password_btn = tk.Button(password_frame, text="👁", font=("Arial", 10), relief="flat", bd=0, cursor="hand2", command=self.toggle_password)
        self.show_password_btn.pack(side="right", padx=(0, 5))


        # LOGIN Button - Centered
        login_btn = ttk.Button(login_frame, text="LOGIN", command=self.login, width=20)
        login_btn.pack(pady=15)

        # Forgot Password & Remember Me Frame
        bottom_frame = ttk.Frame(login_frame)
        bottom_frame.pack(fill="x", pady=5)

        # Forgot Password button (Left)
        forgot_password_btn = ttk.Button(bottom_frame, text="Forgot Password?", command=self.reset_password)
        forgot_password_btn.pack(side="left", padx=(0, 50))

        # Remember Me checkbox (Right)
        self.remember_me_var = tk.BooleanVar()
        remember_me_check = ttk.Checkbutton(bottom_frame, text="Remember Me", variable=self.remember_me_var)
        remember_me_check.pack(side="right")

         # Initialize Welcome Message Label (Initially Hidden)
        self.welcome_label = ttk.Label(login_frame, text="", font=("Arial", 12, "bold"), foreground="green")
        self.welcome_label.pack(pady=5)
        self.client_data = {} 

    def create_entry(self, parent, placeholder, show=None):
        """Creates an entry field with placeholder text."""
        entry = ttk.Entry(parent, show=show, font=("Arial", 11))  # Remove width, use fill="x" instead
        entry.insert(0, placeholder)  # Insert placeholder text
        entry.bind("<FocusIn>", self.clear_placeholder)
        entry.bind("<FocusOut>", self.restore_placeholder)
        return entry

    def clear_placeholder(self, event):
        """Clears the placeholder text when the user clicks into the entry."""
        if event.widget.get() == event.widget.get():
            event.widget.delete(0, "end")
            event.widget.config(foreground='black')

    def restore_placeholder(self, event):
        """Restores the placeholder text if the entry is empty."""
        if event.widget.get() == "":
            event.widget.insert(0, event.widget._placeholder)
            event.widget.config(foreground='gray')

    def toggle_password(self):
        """Toggle password visibility."""
        if self.password_entry.cget('show') == '*':
            self.password_entry.config(show='')
            self.show_password_btn.config(text='🙈')  # Change text to hide password
        else:
            self.password_entry.config(show='*')
            self.show_password_btn.config(text='👁')  # Change text to show password

    def login(self):
        """Dummy login function."""
        messagebox.showinfo("Login", "Login clicked")

    def reset_password(self):
        """Dummy reset password function."""
        messagebox.showinfo("Reset Password", "Reset Password clicked")
    def fetch_data(self, endpoint, params=None):
        """Fetch data from API with proper parameter handling."""
        try:
            response = requests.get(endpoint, params=params, timeout=5)
            if response.status_code == 200:
                return response.json().get("content", {}).get("data", [])
            else:
                messagebox.showerror("Error", f"Failed to fetch data: {response.status_code}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Request failed: {e}")
        return []   
    def account_fetch_data(self, endpoint, params=None):#the method should return the full response instead of just data.
        """Fetch data from API with proper error handling."""
        try:
            response = requests.get(endpoint, params=params, timeout=5)
            if response.status_code == 200:
                return response.json()  # ✅ Return full response instead of only `data`
            else:
                messagebox.showerror("Error", f"Failed to fetch data: {response.status_code}")
                return {"status_code": response.status_code, "content": {"data": []}}
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Request failed: {e}")
            return {"status_code": 500, "content": {"data": []}}  # ✅ Return empty dict on failure

    def login(self):
        """Authenticate user via API in a separate thread."""
        email = self.email_entry.get()
        password = self.password_entry.get()
        payload = {"email": email, "password": password}

    def login(self):
        """Trigger login in a separate thread."""
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
                        self.root.after(0, lambda: self.show_welcome_message(username))
                        self.root.after(0, lambda: self.open_selection_window())

                    else:
                        self.root.after(0, lambda: messagebox.showerror("Error", "Invalid credentials"))
                else:
                    self.root.after(0, lambda: messagebox.showerror("Error", "Invalid email or password"))
            except requests.exceptions.RequestException as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Request failed: {e}"))

        threading.Thread(target=login_request, daemon=True).start()

    def show_welcome_message(self, username):
        self.root.after(1000, self.root.withdraw)  # Hide login window after 10 sec
        """Display welcome message in the UI."""
        self.welcome_label.config(text=f"Welcome, {username}!")
        self.email_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

    def open_selection_window(self):
        # """Opens selection window for clients, portals, and accounts."""
        self.selection_window = tk.Toplevel()
        self.selection_window.title("Select Client Details")
        self.selection_window.geometry("450x500")
        self.selection_window.resizable(False, False)

        # Create a centered frame inside the window
        frame = ttk.Frame(self.selection_window, padding=20)
        frame.pack(expand=True)  # Center frame in the window

        # Label Styling
        label_font = ("Arial", 11)
        input_width = 30
        padding = {'pady': 5, 'padx': 10}

        # Main Client Dropdown
        ttk.Label(frame, text="Main Client:", font=label_font).pack(anchor="center", **padding)
        self.main_client_var = tk.StringVar()
        self.main_client_dropdown = ttk.Combobox(frame, textvariable=self.main_client_var, width=input_width)
        self.main_client_dropdown.pack(**padding)
        self.main_client_dropdown.bind("<<ComboboxSelected>>", self.on_main_client_select)

        # Sub Client Dropdown
        ttk.Label(frame, text="Sub Client:", font=label_font).pack(anchor="center", **padding)
        self.sub_client_var = tk.StringVar()
        self.sub_client_dropdown = ttk.Combobox(frame, textvariable=self.sub_client_var, width=input_width)
        self.sub_client_dropdown.pack(**padding)
        self.sub_client_dropdown.bind("<<ComboboxSelected>>", self.on_sub_client_select)

        # Portal Dropdown
        ttk.Label(frame, text="Portal:", font=label_font).pack(anchor="center", **padding)
        self.portal_var = tk.StringVar()
        self.portal_dropdown = ttk.Combobox(frame, textvariable=self.portal_var, width=input_width)
        self.portal_dropdown.pack(**padding)
        self.portal_dropdown.bind("<<ComboboxSelected>>", self.on_portal_select)

        # Account Dropdown
        ttk.Label(frame, text="Select Account:", font=label_font).pack(anchor="center", **padding)
        self.account_var = tk.StringVar()
        self.account_dropdown = ttk.Combobox(frame, textvariable=self.account_var, width=input_width)
        self.account_dropdown.pack(**padding)

        # Login Button
        self.login_button = ttk.Button(frame, text="Login to Portal", command=self.confirm_selection, width=20)
        self.login_button.pack(pady=15)

        # Load clients in a separate thread
        threading.Thread(target=self.load_main_clients, daemon=True).start()

    def load_main_clients(self):
        """Fetch and populate main clients."""
        self.client_data["main_clients"] = self.fetch_data(MAIN_CLIENTS_API)
        self.main_client_dropdown["values"] = [c["client_name"] for c in self.client_data["main_clients"]]

    def on_main_client_select(self, event):
        """Handle main client selection."""
        selected_client = next((c for c in self.client_data["main_clients"] if c["client_name"] == self.main_client_var.get()), None)
        if selected_client:
            client_id = selected_client["id"]
            threading.Thread(target=self.load_sub_clients, args=(client_id,), daemon=True).start()

    def load_sub_clients(self, client_id):
        """Fetch and populate sub-clients."""
        self.client_data["sub_clients"] = self.fetch_data(SUB_CLIENTS_API)
        self.sub_client_dropdown["values"] = [sc["client_name"] for sc in self.client_data["sub_clients"]]

    def on_sub_client_select(self, event):
        """Handle sub-client selection and store `sub_client_id` for later use."""
        selected_sub_client = next((sc for sc in self.client_data["sub_clients"] if sc["client_name"] == self.sub_client_var.get()), None)
        
        if selected_sub_client:
            self.selected_sub_client_id = selected_sub_client["id"]  # ✅ Store sub-client ID
            threading.Thread(target=self.load_portals, args=(self.selected_sub_client_id,), daemon=True).start()

    def load_portals(self, sub_client_id):
        """Fetch portals using sub-client ID and store for later use in accounts."""
        portals = self.fetch_data(PORTALS_API, {"client_id": sub_client_id})
        
        if portals:
            self.client_data["portals"] = portals
            self.portal_dropdown["values"] = [p["portal_name"] for p in portals]
        else:
            messagebox.showinfo("No Portals", "No portals found for the selected sub-client.")

    def on_portal_select(self, event):
        """Handle portal selection and fetch accounts using `sub_client_id` & `portal_id`."""
        selected_portal = next((p for p in self.client_data["portals"] if p["portal_name"] == self.portal_var.get()), None)
        
        if selected_portal:
            self.selected_portal_id = selected_portal["portal_id"]  # Store portal ID
            self.selected_portal_url = selected_portal["portal_url"]  #  Store portal URL

            # Fetch accounts using both `sub_client_id` & `portal_id`
            threading.Thread(target=self.load_account_info, args=(self.selected_sub_client_id, self.selected_portal_id), daemon=True).start()

    def load_account_info(self, sub_client_id, portal_id):
        """Fetch accounts using sub-client ID and portal ID, without pre-selecting."""
        response = self.account_fetch_data(ACCOUNT_API, {"client_id": sub_client_id, "portal_id": portal_id})
        print(response)
        # Ensure response is a dictionary and has status_code
        if isinstance(response, dict) and response.get("status_code") == 200:
            content = response.get("content", {})

            # Ensure `content` is a dictionary before accessing "data"
            if isinstance(content, dict):
                accounts = content.get("data", [])

                if isinstance(accounts, list) and accounts:  # Ensure accounts is a list
                    self.accounts = accounts  # Store accounts for selection
                    
                    # Populate dropdown with account_id but display username
                    self.account_dropdown["values"] = [str(acc["account_id"]) for acc in accounts]

                    #  Do NOT pre-select an account
                    self.account_var.set("")  # Keep dropdown empty until user selects
                    
                else:
                    messagebox.showinfo("No Accounts", "No accounts found for the selected portal and sub-client.")
            else:
                messagebox.showerror("Error", "Invalid response format: 'content' is missing or incorrect.")
        else:
            messagebox.showerror("Error", "Failed to fetch account information.")

    def on_account_select(self, event):
        """Handle account selection and update details."""
        selected_account_id = self.account_var.get()
        selected_account = next((acc for acc in self.accounts if str(acc["account_id"]) == selected_account_id), None)
        if selected_account:
            self.load_selected_account_info(selected_account)

    def load_selected_account_info(self, account):
        """Load and display details for the selected account."""
        self.username_label.config(text=f"Username: {account['username']}")
        self.password_label.config(text=f"Password: {account['password']}")
        self.session_label.config(text=f"Session: {account['session']}")
        self.portal_url_label.config(text=f"Portal URL: {self.selected_portal_url}")


    def confirm_selection(self):
        """Confirm client details selection and trigger login."""
        main_client = self.main_client_var.get()
        sub_client = self.sub_client_var.get()
        portal = self.portal_var.get()
        account = self.account_var.get()
        
        if main_client and sub_client and portal and account:
            # Find the selected account based on username
            selected_account = next((acc for acc in self.accounts if acc["account_id"] == int(account)), None)

            
            if selected_account:
                # Trigger the login function with the selected account details
                self.login_to_portal(selected_account)
            else:
                messagebox.showerror("Error", "Selected account not found.")
        else:
            messagebox.showwarning("Incomplete Selection", "Please select all details to proceed.")

    def login_to_portal(self, selected_account):
        """Login to the portal with the selected account details."""
        portal = self.portal_var.get()
        if portal:
            portal_login = PortalLogin(self.client_data)
            threading.Thread(
                target=portal_login.login_to_portal,
                args=(selected_account["username"], selected_account["password"], self.selected_portal_url, portal),
                daemon=True
            ).start()

        else:
            messagebox.showerror("Error", "Portal login function not found.")

    # def ui_callback(self, title, message):
    #     """Update the UI based on login status."""
    #     messagebox.showinfo(title, message)

    #     # Re-enable the login button after the operation
    #     self.login_button.config(state=NORMAL)

    # def login_to_portal(self):
    #     """Log in to selected portal."""
    #     if hasattr(self, 'login_function'):
    #         self.login_function()  # Call the appropriate portal login function
    #     else:
    #         messagebox.showerror("Error", "Please select a portal first.")        

# Create main window
# root = tk.Tk()
# app = UserSelectionApp(root)
# root.mainloop()
