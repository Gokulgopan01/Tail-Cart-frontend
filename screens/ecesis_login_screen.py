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
from utils.helper import params_check, setup_driver
from utils.user_data import save_login_data, load_login_data
from config import env
from utils.glogger import GLogger
logger = GLogger()
# Load variables from .env file

load_dotenv()

# Retrieve API URLs from environment variables
BASE_URL = env.BASE_URL
LOGIN_API = env.LOGIN_API

# Construct API endpoints dynamically
MAIN_CLIENTS_API = f"{BASE_URL}/getMainClients"
SUB_CLIENTS_API = f"{BASE_URL}/getSubclientByMainClient"
PORTALS_API = f"{BASE_URL}/getClientPortals"
ACCOUNT_API = f"{BASE_URL}/getAccountInfo"

#Print API URLs (Remove in Production)
print(f"Main Clients API: {MAIN_CLIENTS_API}")
print(f"Login API: {LOGIN_API}")

arg1, arg2,arg3 = params_check()  # Extract parameters at the top






class EcesisLoginScreen(tk.Frame):

    def __init__(self,parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.active_portal_instances = []
        # Load Image

        img_path = resource_path("settings.jpg")
        image = Image.open(img_path)
        image = image.resize((30, 30))  # Resize if needed
        self.settings_logo = ImageTk.PhotoImage(image)
        # Set the window icon

        self.top_frame = tk.Frame(self, bg="white")
        self.top_frame.pack(fill="x", side="top")
        style = ttk.Style()
        style.configure("Custom.TButton", background="white", relief="flat")
        btn = ttk.Button(self.top_frame, image=self.settings_logo, command=lambda: controller.show_frame("SettingsScreen"),style="Custom.TButton",cursor="hand2")
        btn.pack(side="right", padx=5, pady=5)
        #btn.image = self.settings_logo
        # 2. Version Label (Packs left of the button)
        # ✨ CHANGE: Uses self.app_version (which holds "1.1")
        self.version_label = tk.Label(
            self.top_frame,
            text=f"Version: {env.VERSION_FILE}",
            bg="white",
            fg="#333333",
            font=("Arial", 9)
        )
        self.version_label.pack(side="right", padx=5, pady=5)
        """Create a login UI with a dark blue, yellow, and white color scheme."""
        self.login_frame = tk.Frame(self, bg="#FFFFFF")  # White
        self.login_frame.pack(fill="both", expand=True)

        # Now create the LabelFrame with the correct style
        self.input_frame = ttk.LabelFrame(self.login_frame, padding=10, style="Custom.TLabelframe")
        self.input_frame.pack(pady=30, padx=20, ipadx=10, fill="x")
        # Initialize client data
        self.client_data = {}
        self.create_login_frame()

    def create_login_frame(self):


#         logger.log(
#     module="OtherModule",
#     order_id="123",
#     action_type="step_done",
#     remarks="Step completed successfully",
#     severity="INFO"
# )

        # ttk.Label(self.login_frame, text="ECESIS", font=("sans-serif", 14, "bold"), background="#FFFFFF").pack(pady=10)
        ttk.Label(self.login_frame, text="HYBRID CLIENT LOGIN", font=("sans-serif", 16, "bold"), background="#FFFFFF").pack(pady=20)
        ttk.Label(self.login_frame, text="Welcome back! Please login to your account to continue", font=("sans-serif", 10), background="#FFFFFF").pack(pady=5)

        # # Use a Frame instead of ttk.LabelFrame
        self.input_frame = tk.Frame(self.login_frame, bg="#FFFFFF", relief="solid", padx=60, pady=20)
        self.input_frame.pack(pady=10, padx=20)

        # Email Entry Frame with Border
        self.border_frame = tk.Frame(self.input_frame, relief="solid", bg="white")
        self.border_frame.pack(pady=6, ipady=3, fill="both")

        # Email Entry with a Border (Using tk.Entry instead of ttk.Entry)
        self.email_var = tk.StringVar()
        self.email_entry = tk.Entry(self.border_frame, font=("sans-serif", 11), textvariable=self.email_var, foreground="gray", background="white", width=50)
        self.email_entry.pack(pady=0, ipady=8, fill="both", expand=True)
        self.email_var.set("Enter your email")

        # Add a border around the email entry field
        self.email_entry.config(highlightthickness=1, highlightbackground="#333333", highlightcolor="black")

        # Bind Enter key to focus on the password field when Enter is pressed
        self.email_entry.bind("<Return>", lambda event: self.password_entry.focus_set())

        # Password Entry Frame
        self.password_frame = tk.Frame(self.input_frame, relief="solid", bg="white", bd=1, height=150)
        self.password_frame.pack(pady=8, ipady=4, fill="both")

        # Password Entry (No Label)
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(self.password_frame, font=("sans-serif", 11), textvariable=self.password_var, foreground="gray", background="white", relief="flat")
        self.password_entry.pack(side="left", fill="both", expand=True, padx=(1, 0))
        self.password_var.set("Enter your password")


        # # Toggle Button Inside the Password Box
        self.show_password_btn = tk.Button(self.password_frame, text="👁", font=("sans-serif", 13), relief="flat", cursor="hand2", bg="white", command=self.toggle_password)
        self.show_password_btn.pack(side="right", padx=(0, 3))



        canvas = tk.Canvas(self.input_frame, width=200, height=50, bg="#FFFFFF", highlightthickness=0,cursor="hand2")
        canvas.pack(pady=30)

        # Draw rounded rectangle (simplified)
        x0, y0, x1, y1 = 10, 10, 190, 50
        r = 20  # corner radius
        button = canvas.create_arc(x0, y0, x0+r*2, y0+r*2, start=90, extent=90, fill="#1877F2", outline="#1877F2")
        canvas.create_arc(x1-r*2, y0, x1, y0+r*2, start=0, extent=90, fill="#1877F2", outline="#1877F2")
        canvas.create_arc(x0, y1-r*2, x0+r*2, y1, start=180, extent=90, fill="#1877F2", outline="#1877F2")
        canvas.create_arc(x1-r*2, y1-r*2, x1, y1, start=270, extent=90, fill="#1877F2", outline="#1877F2")
        canvas.create_rectangle(x0+r, y0, x1-r, y1, fill="#1877F2", outline="#1877F2")
        canvas.create_rectangle(x0, y0+r, x1, y1-r, fill="#1877F2", outline="#1877F2")

        text = canvas.create_text((x0 + x1)//2, (y0 + y1)//2, text="Login", fill="white", font=("sans-serif", 13, "bold"))

        # Bind click
        canvas.bind("<Button-1>", lambda event: self.login())

            # Enter key triggers login from anywhere in the login frame
        #self.login_frame.bind_all("<Return>", self.login())

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


        bottom_frame = tk.Frame(self, bg="white")
        bottom_frame.pack(fill="x", side="bottom")
        copyright_label = tk.Label(
            bottom_frame,
            text="Copyright © 2025 Ecesis. All rights reserved.",
            font=("Arial", 9),
            bg='white',
            fg="gray"
        )
        copyright_label.pack(side="bottom", pady=5, padx=5)


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

        # def login_request():
        #     try:
        #         response = requests.post(LOGIN_API, json=payload, timeout=5)
        #         if response.status_code == 200:
        #             data = response.json()
        #             if data.get("status_code") == 200 and data.get("content", {}).get("data", {}).get("success"):
        #                 username = data["content"]["data"]["username"]
        #                 self.after(0, lambda: self.show_client_login(username))
        #                 token = data["content"]["data"]["token"]
        #                 user_details = data["content"]["data"]
        #                 logged_in = True
        #                 # store the data:
        #                 save_login_data(logged_in,token,user_details)
        # 
        #             else:
        #                 self.after(0, lambda: messagebox.showerror("Error", "Invalid credentials"))
        #         else:
        #             self.after(0, lambda: messagebox.showerror("Error", "Invalid email or password"))
        #     except requests.exceptions.RequestException as e:
        #         self.after(0, lambda: messagebox.showerror("Error", f"Request failed: {e}"))

        # threading.Thread(target=login_request, daemon=True).start()
        
        #arg1="SmartEntry"
        #arg1="PortalLogin"
        #arg1="AutoLogin"
        # Inside your login function
        def login_request():
            try:
                response = requests.post(LOGIN_API, json=payload, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status_code") == 200 and data["content"]["data"].get("success"):
                        username = data["content"]["data"]["username"]
                        token = data["content"]["data"]["token"]
                        user_details = data["content"]["data"]
                        logged_in = True

                        # #  Save token and details
                        # save_login_data(logged_in, token, user_details)

                        # # Update UI in main thread
                        # self.after(0, lambda: self.show_welcome_message(username))
                        #self.after(0, self.close_login_screen)  
                        # Conditionally show client selection screen
                        if arg1 not in ["PortalLogin", "SmartEntry"]:
                            self.after(0, lambda: self.show_client_login(username))
                            save_login_data(logged_in, token, user_details)
                        else:
                                #  Save token and details
                            #save_login_data(logged_in, token, user_details)

                            # Update UI in main thread
                            self.after(0, lambda: self.show_welcome_message(username))
                            self.after(0, self.close_login_screen)  # close popup if used in modal

                    else:
                        self.after(0, lambda: messagebox.showerror("Error", "Invalid credentials"))
                else:
                    self.after(0, lambda: messagebox.showerror("Error", "Invalid email or password"))
            except requests.exceptions.RequestException as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Request failed: {e}"))

        # Start the login request in a background thread
        threading.Thread(target=login_request, daemon=True).start()

    def close_login_screen(self):
        """Destroy the login popup frame (only used when run as modal popup)"""
        self.winfo_toplevel().destroy()
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
        # if hasattr(self, "login_frame"):
        #     self.login_frame.pack_forget()  # Hide the login frame
        # #  Initialize labels
        self.username_label = ttk.Label(self, text="Username: ")
        self.password_label = ttk.Label(self, text="Password: ")
        self.session_label = ttk.Label(self, text="Session: ")
        self.portal_url_label = ttk.Label(self, text="Portal URL: ")
        self.proxy_label=ttk.Label(self, text="Proxy: ")
        
    
        # Set background color
        self.configure(bg="#FFFFFF")  # Light Gray Background
    
        self.logout_button_top = tk.Button(self.top_frame, text="Logout", command=self.logout,
                                        font=("Arial", 10, "bold"), fg="white", bg="#FF5630",
                                        bd=0, relief="flat", height=1, width=10)
        self.logout_button_top.pack(side='right',padx=10, pady=7)

    #     # Main client frame
        self.client_frame = tk.Frame(self, bg="#FFFFFF")
        self.client_frame.pack(fill="x", expand=True)

        # Inner Frame (White Box)
        self.inner_frame = tk.Frame(self.client_frame, bg="white", relief="solid")
        self.inner_frame.pack(padx=(175,160),fill="both", expand=True)

        # Welcome Message
        ttk.Label(self.inner_frame, text=f"Welcome, {username}!", font=("sans-serif", 16), background="white").pack(pady=(10, 15))
        ttk.Label(self.inner_frame, text="Select Client Details", font=("sans-serif", 14), background="white").pack(pady=(0, 20))

        # Main Client Dropdown
        self.main_client_var = tk.StringVar()
        style = ttk.Style()
        style.configure('TCombobox', padding=5, font=('sans-serif', 13), height=30)
        self.main_client_dropdown = self.create_combobox(self.inner_frame, self.main_client_var, "Select Mainclient", self.on_main_client_select)
        self.main_client_dropdown.config(style='TCombobox')
        self.main_client_dropdown.pack(pady=8, padx=30, fill='x')
        self.main_client_dropdown.bind("<Return>", lambda event: self.sub_client_dropdown.focus_set())  # Move to Sub Client

    

    #     # Sub Client Dropdown
        self.sub_client_var = tk.StringVar()
        style = ttk.Style()
        style.configure('TCombobox', padding=5, font=('sans-serif', 13), height=30)
        self.sub_client_dropdown = self.create_combobox(self.inner_frame, self.sub_client_var, "Select Subclient", self.on_sub_client_select)
        self.sub_client_dropdown.config(style='TCombobox')
        self.sub_client_dropdown.pack(pady=8, padx=30, fill='x')
        self.sub_client_dropdown.bind("<Return>", lambda event: self.portal_dropdown.focus_set())  # Move to Portal

    #     # Portal Dropdown
        self.portal_var = tk.StringVar()
        style = ttk.Style()
        style.configure('TCombobox', padding=5, font=('sans-serif', 13), height=30)
        self.portal_dropdown = self.create_combobox(self.inner_frame, self.portal_var, "Select Portal", self.on_portal_select)
        self.portal_dropdown.config(style='TCombobox')
        self.portal_dropdown.pack(pady=8, padx=30, fill='x')
        self.portal_dropdown.bind("<Return>", lambda event: self.account_dropdown.focus_set())  # Move to Account
    # # Move to the Login Button


    #     # Account Dropdown
        self.account_var = tk.StringVar()
        style = ttk.Style()
        style.configure('TCombobox', padding=5, font=('sans-serif', 13), height=30)
        self.account_dropdown = self.create_combobox(self.inner_frame, self.account_var, "Select Account", self.on_account_select)
        self.account_dropdown.config(style='TCombobox')
        self.account_dropdown.pack(pady=8, padx=30, fill='x')
        self.account_dropdown.bind("<Return>", lambda event: self.confirm_selection())  # Move to the Login Button

    #     # Login Button

        canvas = tk.Canvas(self.inner_frame, width=200, height=100, bg="#FFFFFF", highlightthickness=0,cursor="hand2")
        canvas.pack(pady=30)

        # Draw rounded rectangle (simplified)
        x0, y0, x1, y1 = 10, 10, 190, 50
        r = 20  # corner radius
        button = canvas.create_arc(x0, y0, x0+r*2, y0+r*2, start=90, extent=90, fill="#1877F2", outline="#1877F2")
        canvas.create_arc(x1-r*2, y0, x1, y0+r*2, start=0, extent=90, fill="#1877F2", outline="#1877F2")
        canvas.create_arc(x0, y1-r*2, x0+r*2, y1, start=180, extent=90, fill="#1877F2", outline="#1877F2")
        canvas.create_arc(x1-r*2, y1-r*2, x1, y1, start=270, extent=90, fill="#1877F2", outline="#1877F2")
        canvas.create_rectangle(x0+r, y0, x1-r, y1, fill="#1877F2", outline="#1877F2")
        canvas.create_rectangle(x0, y0+r, x1, y1-r, fill="#1877F2", outline="#1877F2")

        text = canvas.create_text((x0 + x1)//2, (y0 + y1)//2, text="Login to Portal", fill="white", font=("sans-serif", 13, "bold"))

        # Bind click
        canvas.bind("<Button-1>", lambda event: self.confirm_selection())
      

        threading.Thread(target=self.load_main_clients, daemon=True).start()

   

    def create_combobox(self, parent, var, placeholder, callback):
        """Create a custom searchable dropdown with Entry + Listbox that mimics ttk.Combobox."""
        
        class AutocompleteCombobox(tk.Frame):
            """Custom combobox widget using Entry + Listbox with proper popup positioning."""
            def __init__(self, parent_widget, textvariable, placeholder_text, selection_callback):
                # Container behavior
                super().__init__(parent_widget, bg='white', highlightthickness=1, highlightbackground='#CCCCCC')
                
                self._var = textvariable
                self._placeholder = placeholder_text
                self._callback = selection_callback
                self._all_values = []
                
                # Layout
                # Entry widget on the left
                self._entry = tk.Entry(self, textvariable=textvariable, font=('sans-serif', 12),
                                      bd=0, bg='white')
                self._entry.pack(side=tk.LEFT, padx=(5, 0), pady=5, fill=tk.X, expand=True)
                
                # Initial placeholder
                if not textvariable.get():
                    self._entry.insert(0, placeholder_text)
                    self._entry.config(fg='gray')
                else:
                    self._entry.config(fg='black')
                
                # Dropdown arrow on the right
                self._arrow = tk.Label(self, text="▼", font=('Arial', 8), bg='white', 
                                      fg='#666666', width=2, cursor='hand2')
                self._arrow.pack(side=tk.RIGHT, padx=5)
                
                # Popup Listbox (Using Toplevel for "floating" behavior)
                self._popup = tk.Toplevel(self)
                self._popup.withdraw()
                self._popup.overrideredirect(True)
                self._popup.config(relief=tk.SOLID, bd=1)
                
                self._listbox = tk.Listbox(self._popup, font=('sans-serif', 11),
                                          selectbackground='#0078d7', bd=0, highlightthickness=0)
                self._scrollbar = tk.Scrollbar(self._popup, orient=tk.VERTICAL, command=self._listbox.yview)
                self._listbox.config(yscrollcommand=self._scrollbar.set)
                
                self._listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                
                # Binds
                self._arrow.bind('<Button-1>', lambda e: self.toggle_dropdown())
                self._entry.bind('<FocusIn>', self._on_focus_in)
                self._entry.bind('<FocusOut>', self._on_focus_out)
                self._listbox.bind('<<ListboxSelect>>', self._on_listbox_select)
                self._listbox.bind('<Button-1>', self._on_listbox_select)

            def _on_focus_in(self, event):
                if self._entry.get() == self._placeholder:
                    self._entry.delete(0, tk.END)
                    self._entry.config(fg='black')

            def _on_focus_out(self, event):
                # Use after to check focus after it settles
                self.after(200, self._check_focus_out)

            def _check_focus_out(self):
                # If focus didn't move to the popup/listbox, handle placeholder
                focus_widget = self.focus_get()
                if focus_widget != self._listbox and focus_widget != self._popup:
                    if not self._entry.get():
                        self._entry.insert(0, self._placeholder)
                        self._entry.config(fg='gray')
                    self._popup.withdraw()

            def toggle_dropdown(self):
                if self._popup.winfo_ismapped():
                    self._popup.withdraw()
                else:
                    self.show_results(self._all_values)

            def show_results(self, values):
                if not values:
                    self._popup.withdraw()
                    return
                
                self._listbox.delete(0, tk.END)
                for v in values:
                    self._listbox.insert(tk.END, v)
                
                # Positioning
                self.update_idletasks()
                x = self.winfo_rootx()
                y = self.winfo_rooty() + self.winfo_height()
                width = self.winfo_width()
                # Dynamic height based on content
                height = min(len(values) * 22 + 5, 200) 
                
                self._popup.geometry(f"{width}x{height}+{x}+{y}")
                self._popup.deiconify()
                self._popup.lift()
                
                # Highlight first
                self._listbox.selection_clear(0, tk.END)
                self._listbox.selection_set(0)
                self._listbox.activate(0)

            def _on_listbox_select(self, event):
                selection = self._listbox.curselection()
                if selection:
                    val = self._listbox.get(selection[0])
                    self.set(val)
                    self._popup.withdraw()
                    if self._callback:
                        self._callback(event)
            
            def __setitem__(self, key, value):
                if key == "values":
                    self._all_values = value
                # Ignore other keys to prevent TclErrors

            def __getitem__(self, key):
                if key == "values":
                    return self._all_values
                return None

            def set(self, text):
                self._entry.delete(0, tk.END)
                self._entry.insert(0, text)
                self._entry.config(fg='black')

            def get(self):
                return self._entry.get()

            def focus_set(self):
                self._entry.focus_set()

            def bind(self, event, handler):
                self._entry.bind(event, handler)
            
            def config(self, **kwargs):
                pass # Support config calls like style

        return AutocompleteCombobox(parent, var, placeholder, callback)


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

    def bind_dropdown_keyboard_sort(self, container, values_list, default_text="Select"):
        """Adds live search filtration to custom Entry+Listbox dropdown."""
        sorted_values = sorted([str(v) for v in values_list])
        container._all_values = sorted_values
        
        def on_keyrelease(event):
            # Ignore special keys
            if event.keysym in ("Down", "Up", "Return", "Escape", "Tab", "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R"):
                return
            
            value = container.get()
            
            # Skip if placeholder
            if value == container._placeholder or value == "":
                container._popup.withdraw()
                return
            
            # Filter data
            lower_val = value.lower()
            starts_with = [item for item in sorted_values if item.lower().startswith(lower_val)]
            contains = [item for item in sorted_values if lower_val in item.lower() and item not in starts_with]
            filtered_data = starts_with + contains
            
            container.show_results(filtered_data)
        
        def on_return(event):
            """Press Enter to select top result."""
            if container._popup.winfo_ismapped() and container._listbox.size() > 0:
                # Use current selection if any, else first
                selection = container._listbox.curselection()
                idx = selection[0] if selection else 0
                val = container._listbox.get(idx)
                container.set(val)
                container._popup.withdraw()
                if container._callback:
                    container._callback(event)
                return "break"
        
        def on_down(event):
            """Navigate dropdown list with arrow keys."""
            if container._popup.winfo_ismapped():
                current = container._listbox.curselection()
                next_idx = min(current[0] + 1, container._listbox.size() - 1) if current else 0
                container._listbox.selection_clear(0, tk.END)
                container._listbox.selection_set(next_idx)
                container._listbox.activate(next_idx)
                container._listbox.see(next_idx)
                return "break"
            else:
                container.show_results(container._all_values)
                return "break"

        def on_up(event):
            """Navigate dropdown list with arrow keys."""
            if container._popup.winfo_ismapped():
                current = container._listbox.curselection()
                prev_idx = max(current[0] - 1, 0) if current else 0
                container._listbox.selection_clear(0, tk.END)
                container._listbox.selection_set(prev_idx)
                container._listbox.activate(prev_idx)
                container._listbox.see(prev_idx)
                return "break"
        
        def on_escape(event):
            container._popup.withdraw()
            
        # Bind events
        container.bind('<KeyRelease>', on_keyrelease)
        container.bind('<Return>', on_return)
        container.bind('<Down>', on_down)
        container.bind('<Up>', on_up)
        container.bind('<Escape>', on_escape)

    def load_main_clients(self):
        """Fetch and populate main clients."""
        response = self.fetch_data(MAIN_CLIENTS_API)
        if response:
            self.client_data["main_clients"] = response
            values_list = sorted([c["client_name"] for c in self.client_data["main_clients"]])
            self.main_client_dropdown["values"] = values_list
            self.bind_dropdown_keyboard_sort(self.main_client_dropdown, values_list, "Select Main Client")


    def on_main_client_select(self, event):
        """Handle main client selection and fetch sub-clients."""
        # Reset dependent dropdowns immediately
        self.sub_client_var.set("Select Subclient")
        self.sub_client_dropdown["values"] = []
        self.portal_var.set("Select Portal")
        self.portal_dropdown["values"] = []
        self.account_var.set("Select Account")
        self.account_dropdown["values"] = []

        # Reset labels
        self.username_label.config(text="Username: ")
        self.password_label.config(text="Password: ")
        self.session_label.config(text="Session: ")
        self.portal_url_label.config(text="Portal URL: ")
        self.proxy_label.config(text="Proxy: ")

        # Load sub-clients for selected main client
        selected_client = next(
            (c for c in self.client_data["main_clients"] if c["client_name"] == self.main_client_var.get()), 
            None
        )
        if selected_client:
            client_id = selected_client["id"]
            threading.Thread(target=self.load_sub_clients, args=(client_id,), daemon=True).start()


    def load_sub_clients(self, client_id):
        """Fetch and populate sub-clients."""
        response = self.account_fetch_data(SUB_CLIENTS_API, {"mainClientId": client_id})
        if response and response.get("status_code") == 200 and response.get("content") and response.get("content").get("data"):
            sub_clients_data = response["content"]["data"]
            self.client_data["sub_clients"] = response
            values_list = sorted([sc["client_name"] for sc in sub_clients_data])
            self.sub_client_dropdown["values"] = values_list
            self.bind_dropdown_keyboard_sort(self.sub_client_dropdown, values_list,"Select Subclient")
        else:
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
            values_list = sorted([p["portal_name"] for p in self.client_data["portals"]])
            self.portal_dropdown["values"] = values_list
            self.bind_dropdown_keyboard_sort(self.portal_dropdown, values_list,"Select Portal")


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
            values_list = sorted([str(acc["account_id"]) for acc in self.accounts])
            self.account_dropdown["values"] = values_list
            self.bind_dropdown_keyboard_sort(self.account_dropdown, values_list,"Select Account")


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
                self.login_to_client_portal(selected_account)
            else:
                messagebox.showerror("Error", "Selected account not found.")
        else:
            messagebox.showwarning("Incomplete", "Please select all details to proceed.")


    def login_to_client_portal(self, selected_account):
        """Login to the portal with the selected account details."""
        portal = self.portal_var.get()
        if portal:
            # Instantiate the portal handler class
            portal_instance = PortalLoginScreen.portals(
                selected_account["username"],
                selected_account["password"],
                self.selected_portal_url,
                portal,
                selected_account["proxy"],
                selected_account["session"],
                selected_account["account_id"]
            )
            if portal_instance:
                self.active_portal_instances.append(portal_instance)
                threading.Thread(
                    target=portal_instance.login_to_portal,
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
