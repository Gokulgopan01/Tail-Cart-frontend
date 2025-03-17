import os
import tkinter as tk
from tkinter import DISABLED, NORMAL, ttk, messagebox
import threading
import requests
from portal.Proteck import PortalLogin  #Import the class from proteck.py
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





class UserSelectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ECESIS - Login")
        self.root.geometry("500x600")
        self.root.resizable(False, False)

        # Generate gradient image if not exists
        if not os.path.exists("gradient.png"):
            self.create_gradient_image()

        # Apply background gradient
        self.create_gradient_background()

        # Define styles
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#331A48")
        self.style.configure("TLabel", background="#331A48", foreground="white",
                           font=("Arial", 11))
        self.style.configure("TButton", font=("Arial", 12, "bold"), padding=5, relief="flat")
        self.style.configure("Title.TLabel", foreground="yellow", font=("Arial", 14, "bold"))
        self.style.configure("Welcome.TLabel", foreground="green", font=("Arial", 14, "bold"))

        self.client_data = {}
        self.create_login_frame()

    def create_gradient_image(self, filename="gradient.png", width=500, height=600):
        """Creates a warm gradient background and saves it as an image."""
        gradient = Image.new("RGB", (width, height), "#331A48")
        draw = ImageDraw.Draw(gradient)

        for y in range(height):
            r = int(51 + (255 - 51) * (y / height))
            g = int(26 + (140 - 26) * (y / height))
            b = int(72 + (100 - 72) * (y / height))
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        gradient.save(filename)
        print(f"Gradient saved as {filename}")

    def create_gradient_background(self):
        """Load the generated gradient image and set it as the background."""
        self.canvas = tk.Canvas(self.root, width=500, height=600)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # Load gradient image
        self.gradient_bg = Image.open("gradient.png").resize((500, 600))
        self.gradient_bg = ImageTk.PhotoImage(self.gradient_bg)
        self.canvas.create_image(0, 0, anchor="nw", image=self.gradient_bg)

    def create_login_frame(self):
        """Create a modern login UI with rounded fields and gradient buttons."""
        """Create a login frame that fills the entire window."""
        self.login_frame = ttk.Frame(self.root, style="TFrame") # create frame
        self.login_frame.place(relwidth=1, relheight=1) # fill the window
        self.login_frame = tk.Frame(self.root, bg="#331A48")
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Welcome text
        ttk.Label(self.login_frame, text="Welcome back", font=("Arial", 18, "bold"),
                  foreground="white", background="#331A48").pack(pady=5)
        ttk.Label(self.login_frame, text="Please Enter your Account details", font=("Arial", 10),
                  foreground="gray", background="#331A48").pack(pady=5)

        # Email Input
        ttk.Label(self.login_frame, text="Email", font=("Arial", 10), foreground="white",
                  background="#331A48").pack(anchor="w", padx=10)
        self.email_entry = self.create_rounded_entry("Johndoe@gmail.com")
        self.email_entry.pack(pady=5)

        # Password Input
        ttk.Label(self.login_frame, text="Password", font=("Arial", 10), foreground="white",
                  background="#331A48").pack(anchor="w", padx=10)
        self.password_entry = self.create_rounded_entry("**********", show="*")
        self.password_entry.pack(pady=5)

        # Forgot Password
        forgot_password_frame = tk.Frame(self.login_frame, bg="#331A48")
        forgot_password_frame.pack(pady=10)
        tk.Button(forgot_password_frame, text="Forgot Password", font=("Arial", 9, "bold"), fg="white",
                  bg="#331A48", relief="flat", cursor="hand2", command=self.forgot_password).pack()

        # Login Button
        self.sign_in_btn = tk.Button(self.login_frame, text="Login", font=("Arial", 12, "bold"),
                                     fg="black", bg="#FF8C66", activebackground="#FF5733", bd=0,
                                     relief="flat", height=2, width=15, command=self.login)
        self.sign_in_btn.pack(pady=15)

    def create_rounded_entry(self, placeholder, show=None):
        """Create a rounded entry field with a placeholder and password toggle (no canvas)."""
        entry_frame = ttk.Frame(self.login_frame, padding=(10, 5))
        entry_frame.pack(fill="x")

        # Rounded background for entry
        rounded_bg = ttk.Frame(entry_frame, style="RoundedBg.TFrame")
        rounded_bg.pack(fill="x")

        # Entry Style
        style = ttk.Style()
        style.configure("RoundedEntry.TEntry", fieldbackground="#4A315F", foreground="black",
                        insertcolor="white", borderwidth=0, padding=(5, 5)) # Set insertcolor here
        style.map("RoundedEntry.TEntry",
                fieldbackground=[("focus", "#664A7F"), ("!focus", "#4A315F")])

        entry = ttk.Entry(rounded_bg, font=("Arial", 11), style="RoundedEntry.TEntry", show=show)
        entry.pack(side="left", fill="x", expand=True, padx=(5,0)) # add padx to the entry

        entry.insert(0, placeholder)

        def clear_placeholder(event):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.unbind("<FocusIn>", clear_placeholder_id) # unbind the event

        clear_placeholder_id = entry.bind("<FocusIn>", clear_placeholder)

        # Password Toggle Button (if show is '*')
        if show == '*':
            show_password_btn = ttk.Button(entry, text="👁", style="Toggle.TButton",
                                            command=lambda: toggle())
            show_password_btn.place(relx=1.0, rely=0.5, anchor="e", x=-5) # Place inside entry

            def toggle():
                """Toggle password visibility using closure."""
                if entry.cget('show') == '*':
                    entry.config(show='')
                    show_password_btn.config(text='🙈')
                else:
                    entry.config(show='*')
                    show_password_btn.config(text='👁')

        entry.bind("<Button-1>", lambda event: entry.focus()) # Ensure focus
        entry.focus() # Ensure focus

        return entry

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

    def show_client_login(self, username):
        """Shows the client selection UI after successful login."""
        if hasattr(self, "login_frame"):
            self.login_frame.destroy()
        self.client_frame = ttk.Frame(self.root, style="TFrame")
        self.client_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.inner_frame = ttk.Frame(self.client_frame, padding=20, style="TFrame")
        self.inner_frame.grid(row=0, column=0)

        ttk.Label(self.inner_frame, text=f"Welcome, {username}!", style="Welcome.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 15))
        ttk.Label(self.inner_frame, text="Select Client Details", style="Title.TLabel").grid(row=1, column=0, columnspan=2, pady=(0, 15))

        label_font = ("Arial", 11)
        dropdown_width = 30

        ttk.Label(self.inner_frame, text="Main Client:", font=label_font).grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.main_client_var = tk.StringVar()
        self.main_client_dropdown = ttk.Combobox(self.inner_frame, textvariable=self.main_client_var, width=dropdown_width)
        self.main_client_dropdown.grid(row=2, column=1, padx=10, pady=5)
        self.main_client_dropdown.bind("<<ComboboxSelected>>", self.on_main_client_select)

        ttk.Label(self.inner_frame, text="Sub Client:", font=label_font).grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.sub_client_var = tk.StringVar()
        self.sub_client_dropdown = ttk.Combobox(self.inner_frame, textvariable=self.sub_client_var, width=dropdown_width)
        self.sub_client_dropdown.grid(row=3, column=1, padx=10, pady=5)
        self.sub_client_dropdown.bind("<<ComboboxSelected>>", self.on_sub_client_select)

        ttk.Label(self.inner_frame, text="Portal:", font=label_font).grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.portal_var = tk.StringVar()
        self.portal_dropdown = ttk.Combobox(self.inner_frame, textvariable=self.portal_var, width=dropdown_width)
        self.portal_dropdown.grid(row=4, column=1, padx=10, pady=5)
        self.portal_dropdown.bind("<<ComboboxSelected>>", self.on_portal_select)

        ttk.Label(self.inner_frame, text="Account:", font=label_font).grid(row=5, column=0, sticky="w", padx=10, pady=5)
        self.account_var = tk.StringVar()
        self.account_dropdown = ttk.Combobox(self.inner_frame, textvariable=self.account_var, width=dropdown_width)
        self.account_dropdown.grid(row=5, column=1, padx=10, pady=5)
        self.account_dropdown.bind("<<ComboboxSelected>>", self.on_account_select)

        self.login_button = ttk.Button(self.inner_frame, text="Login to Portal", command=self.confirm_selection)
        self.login_button.grid(row=6, column=0, columnspan=2, pady=15)

        self.logout_button = ttk.Button(self.inner_frame, text="Logout", command=self.logout)
        self.logout_button.grid(row=7, column=0, columnspan=2, pady=5)

        threading.Thread(target=self.load_main_clients, daemon=True).start()

    def logout(self):
        """Logs out and returns to the login screen."""
        self.client_frame.destroy()
        self.create_login_frame()

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
            portal_login = PortalLogin(self.client_data)
            threading.Thread(
                target=portal_login.login_to_portal,
                args=(selected_account["username"], selected_account["password"], self.selected_portal_url, portal),
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
