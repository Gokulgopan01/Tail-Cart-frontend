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

        # img_path = resource_path("settings.jpg")
        # image = Image.open(img_path)
        # image = image.resize((30, 30))  # Resize if needed
        # self.settings_logo = ImageTk.PhotoImage(image)

        self.configure(bg="white")
        # Set the window icon

        # self.top_frame = tk.Frame(self, bg="white")
        # self.top_frame.pack(fill="x", side="top")
        self.top_frame = tk.Frame(self, bg="white") # Light blue to match sky top
        self.top_frame.place(relx=0, rely=0, relwidth=1, height=50)

        # Bottom border for top frame
        self.top_border = tk.Frame(self, height=1, bg="black")
        self.top_border.place(relx=0, y=65, relwidth=1)

        style = ttk.Style()
        style.configure("Custom.TButton", background="white", relief="flat")
        # btn = ttk.Button(self.top_frame, image=self.settings_logo, command=lambda: controller.show_frame("SettingsScreen"),style="Custom.TButton",cursor="hand2")
        # btn.pack(side="right", padx=5, pady=5)
        #btn.image = self.settings_logo
        # 2. Version Label (Packs left of the button)
        # ✨ CHANGE: Uses self.app_version (which holds "1.1")
        self.version_label = tk.Label(
            self.top_frame,
            text=f"Version: {env.VERSION_FILE}",
            bg="white", # Light cloud color fallback
            fg="blue",
            font=("Arial", 9)
        )
        self.version_label.pack(side="right", padx=5, pady=5)
        
        # btn = tk.Button(self.top_frame, image=self.settings_logo, command=lambda: controller.show_frame("SettingsScreen"), bg="#d0e4ff", relief="flat", cursor="hand2")
        # btn.pack(side="right", padx=5, pady=5)
        # self.top_frame.lift()

        """Create a login UI with a dark blue, yellow, and white color scheme."""
        # Main login container (the floating white box)
        self.login_frame = tk.Frame(self, bg="#FFFFFF", padx=40, pady=40)
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.login_frame.lift()

        # Now create the LabelFrame with the correct style
        # self.input_frame = ttk.LabelFrame(self.login_frame, padding=10, style="Custom.TLabelframe")
        # self.input_frame.pack(pady=30, padx=20, ipadx=10, fill="x")
        # Initialize client data
        self.client_data = {}
        self.dropdowns = []
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
        ttk.Label(self.login_frame, text="HYBRID CLIENT LOGIN", font=("sans-serif", 16, "bold"), background="#FFFFFF").pack(pady=(20, 10))
        ttk.Label(self.login_frame, text="Welcome back! Please login to your account to continue", font=("sans-serif", 10), background="#FFFFFF").pack(pady=5)
        
        # # Use a Frame instead of ttk.LabelFrame
        self.input_frame = tk.Frame(self.login_frame, bg="#FFFFFF", padx=60, pady=20)
        self.input_frame.pack(pady=10, padx=20)

        # Email Entry Frame with Border
        self.border_frame = tk.Frame(self.input_frame, relief="flat", bg="white", bd=0)
        self.border_frame.pack(pady=6, ipady=3, fill="both")

        # Email Entry with a Border (Using tk.Entry instead of ttk.Entry)
        self.email_var = tk.StringVar()
        self.email_entry = tk.Entry(self.border_frame, font=("sans-serif", 11), textvariable=self.email_var, foreground="gray", background="white", width=50)
        self.email_entry.pack(pady=0, ipady=8, fill="both", expand=True)
        self.email_var.set("Enter your email")

        # Add a border around the email entry field (Black by default, Gray on focus)
        self.email_entry.config(highlightthickness=1, highlightbackground="black", highlightcolor="#CCCCCC")
        # Bind Enter key to focus on the password field when Enter is pressed
        self.email_entry.bind("<Return>", lambda event: self.password_entry.focus_set())

        # Password Entry Frame (Black border by default)
        self.password_frame = tk.Frame(self.input_frame, relief="flat", bg="white", bd=0, height=150, highlightthickness=1, highlightbackground="black")
        self.password_frame.pack(pady=8, ipady=4, fill="both")

        # Password Entry (No Label)
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(self.password_frame, font=("sans-serif", 11), textvariable=self.password_var, foreground="gray", background="white", relief="flat")
        self.password_entry.pack(side="left", fill="both", expand=True, padx=(1, 0))
        self.password_var.set("Enter your password")

        # Focus bindings to change password frame border (Gray on focus, Gray out-of-focus handled by FocusOut)
        self.password_entry.bind("<FocusIn>", lambda e: self.password_frame.config(highlightbackground="#CCCCCC"))
        self.password_entry.bind("<FocusOut>", lambda e: self.password_frame.config(highlightbackground="black"))
        self.password_entry.bind("<Return>", lambda event: self.login())

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
        canvas.config(takefocus=True)
        canvas.bind("<Return>", lambda event: self.login())

            # Enter key triggers login from anywhere in the login frame
        #self.login_frame.bind_all("<Return>", self.login())

        # Center the elements
        # Removed pack_propagate(False) as we want it to fit content in place mode

        # Bind focus events for placeholder behavior
        self.email_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(self.email_entry, "Enter your email"))
        self.email_entry.bind("<FocusOut>", lambda event: self.restore_placeholder(self.email_entry, "Enter your email"))

        self.password_entry.bind("<FocusIn>", lambda event: self.clear_placeholder(self.password_entry, "Enter your password", hide_text=True))
        self.password_entry.bind("<FocusOut>", lambda event: self.restore_placeholder(self.password_entry, "Enter your password", hide_text=True))

        # Set initial placeholder text AFTER binding events
        self.email_var.set("Enter your email")
        self.password_var.set("Enter your password")


        bottom_frame = tk.Frame(self, bg="white")
        bottom_frame.place(relx=0.5, rely=1.0, y=-10, anchor="s")
        copyright_label = tk.Label(
            bottom_frame,
            text="Copyright © 2025 Ecesis. All rights reserved.",
            font=("Arial", 9),
            bg='white',
            fg="gray"
        )
        copyright_label.pack()
        bottom_frame.lift()



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
        if hasattr(self, "login_frame"):
            self.login_frame.place_forget()
        
        # Initialize labels
        self.username_label = ttk.Label(self, text="Username: ")
        self.password_label = ttk.Label(self, text="Password: ")
        self.session_label = ttk.Label(self, text="Session: ")
        self.portal_url_label = ttk.Label(self, text="Portal URL: ")
        self.proxy_label=ttk.Label(self, text="Proxy: ")
        
        # Set background color - removed to keep sky background visible
        # self.configure(bg="#FFFFFF")
    
        # Create Logout button if it doesn't exist, otherwise just show it
        if not hasattr(self, "logout_button_top") or not self.logout_button_top.winfo_exists():
            self.logout_button_top = tk.Button(self.top_frame, text="Logout", command=self.logout,
                                            font=("Arial", 10, "bold"), fg="white", bg="#FF5630",
                                            bd=0, relief="flat", height=1, width=10)
            self.logout_button_top.pack(side='right',padx=10, pady=7)
        else:
            # Ensure it's packed if it was hidden
            if not self.logout_button_top.winfo_ismapped():
                 self.logout_button_top.pack(side='right',padx=10, pady=7)

        # Main client frame - Reset dropdown tracking list
        self.dropdowns = []
        
        # Destroy old client frame if it exists to prevent overlap/leaks
        if hasattr(self, "client_frame") and self.client_frame.winfo_exists():
            self.client_frame.destroy()
            
        self.client_frame = tk.Frame(self, bg="#FFFFFF")
        self.client_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.7)
        self.inner_frame = tk.Frame(self.client_frame, bg="white", relief="solid")
        self.inner_frame.pack(padx=(50, 50), fill="both", expand=True)

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
        self.dropdowns.append(self.main_client_dropdown)
        # Binding handled in load_main_clients via bind_dropdown_keyboard_sort

    

    #     # Sub Client Dropdown
        self.sub_client_var = tk.StringVar()
        style = ttk.Style()
        style.configure('TCombobox', padding=5, font=('sans-serif', 13), height=30)
        self.sub_client_dropdown = self.create_combobox(self.inner_frame, self.sub_client_var, "Select Subclient", self.on_sub_client_select)
        self.sub_client_dropdown.config(style='TCombobox')
        self.sub_client_dropdown.pack(pady=8, padx=30, fill='x')
        self.dropdowns.append(self.sub_client_dropdown)
        # Binding handled in load_sub_clients via bind_dropdown_keyboard_sort

    #     # Portal Dropdown
        self.portal_var = tk.StringVar()
        style = ttk.Style()
        style.configure('TCombobox', padding=5, font=('sans-serif', 13), height=30)
        self.portal_dropdown = self.create_combobox(self.inner_frame, self.portal_var, "Select Portal", self.on_portal_select)
        self.portal_dropdown.config(style='TCombobox')
        self.portal_dropdown.pack(pady=8, padx=30, fill='x')
        self.dropdowns.append(self.portal_dropdown)
        # Binding handled in load_portals via bind_dropdown_keyboard_sort
    # # Move to the Login Button


    #     # Account Dropdown
        self.account_var = tk.StringVar()
        style = ttk.Style()
        style.configure('TCombobox', padding=5, font=('sans-serif', 13), height=30)
        self.account_dropdown = self.create_combobox(self.inner_frame, self.account_var, "Select Account", self.on_account_select)
        self.account_dropdown.config(style='TCombobox')
        self.account_dropdown.pack(pady=8, padx=30, fill='x')
        self.dropdowns.append(self.account_dropdown)
        # Binding handled in load_accounts via bind_dropdown_keyboard_sort

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
        canvas.config(takefocus=True)
        canvas.bind("<Return>", lambda event: self.confirm_selection())
      

        threading.Thread(target=self.load_main_clients, daemon=True).start()

   

    def create_combobox(self, parent, var, placeholder, callback):
        """Create a custom searchable dropdown with Entry + Listbox that mimics ttk.Combobox."""
        
        class AutocompleteCombobox(tk.Frame):
            """Custom combobox widget using Entry + Listbox with proper popup positioning."""
            def __init__(self, parent_widget, textvariable, placeholder_text, selection_callback, parent_screen=None):
                # Container behavior
                super().__init__(parent_widget, bg='#F0F0F0', highlightthickness=1, highlightbackground='#CCCCCC')
                
                self._var = textvariable
                self._placeholder = placeholder_text
                self._callback = selection_callback
                self._all_values = []
                self._parent_screen = parent_screen
                
                # Layout
                # Entry widget on the left
                self._entry = tk.Entry(self, textvariable=textvariable, font=('sans-serif', 12),
                                      bd=0, bg='#F0F0F0')
                self._entry.pack(side=tk.LEFT, padx=(5, 0), pady=5, fill=tk.X, expand=True)
                
                # Initial placeholder
                if not textvariable.get():
                    self._entry.insert(0, placeholder_text)
                    self._entry.config(fg='gray')
                else:
                    self._entry.config(fg='black')
                
                # Dropdown arrow on the right
                self._arrow = tk.Label(self, text="▼", font=('Arial', 8), bg='#F0F0F0', 
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
                self._entry.bind('<Button-1>', self._on_click)
                self._listbox.bind('<<ListboxSelect>>', self._on_listbox_select)
                self._listbox.bind('<Button-1>', self._on_listbox_select)

            def _on_click(self, event):
                # If it's blue, trigger the same reset logic as FocusIn
                if self.cget('bg') == '#1877F2':
                    self._on_focus_in(event)
                    # SELECTION LOCK: Trigger downstream clear
                    if self._parent_screen:
                        self._parent_screen.reset_downstream(self)

            def _on_focus_in(self, event):
                # If it's blue, reset to gray and select all text for easy re-search
                if self.cget('bg') == '#1877F2':
                    self.set_color_mode('gray')
                    self._entry.selection_range(0, tk.END)
                    self._entry.icursor(tk.END)
                    return 
                
                if self._entry.get() == self._placeholder:
                    self._entry.delete(0, tk.END)
                    # If it's blue, keep text white, otherwise black
                    if self.cget('bg') == '#1877F2':
                        self._entry.config(fg='white')
                    else:
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
                # If it's blue, reset to gray immediately when we open/interact with results
                if self.cget('bg') == '#1877F2':
                    self.set_color_mode('gray')
                    self._entry.selection_range(0, tk.END)

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
                    
                    # Trigger color update in parent screen
                    if self._parent_screen:
                        self._parent_screen.update_dropdown_colors(self)

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
                if self.cget('bg') == '#1877F2':
                    self._entry.config(fg='white')
                else:
                    self._entry.config(fg='black')

            def set_color_mode(self, mode):
                """Update colors based on whether this dropdown is active/selected."""
                if mode == 'blue':
                    bg_color = '#1877F2'
                    fg_color = 'white'
                    border_color = '#1877F2'
                    arrow_fg = 'white'
                else:
                    bg_color = '#F0F0F0'
                    # If it's not a placeholder, use black text
                    current_val = self._entry.get()
                    if current_val == self._placeholder:
                        fg_color = 'gray'
                    else:
                        fg_color = 'black'
                    border_color = '#CCCCCC'
                    arrow_fg = '#666666'
                
                self.config(bg=bg_color, highlightbackground=border_color)
                self._entry.config(bg=bg_color, fg=fg_color)
                self._arrow.config(bg=bg_color, fg=arrow_fg)

            def get(self):
                return self._entry.get()

            def focus_set(self):
                self._entry.focus_set()

            def bind(self, event, handler, add=None):
                self._entry.bind(event, handler, add=add)
            
            def config(self, **kwargs):
                pass # Support config calls like style

        return AutocompleteCombobox(parent, var, placeholder, callback, parent_screen=self)

    def update_dropdown_colors(self, active_dropdown):
        """Sets the selected dropdown to blue and others to gray."""
        for dd in self.dropdowns:
            if dd == active_dropdown:
                dd.set_color_mode('blue')
            else:
                dd.set_color_mode('gray')

    def reset_downstream(self, triggering_dropdown):
        """Clears all dropdowns that depend on the triggering one."""
        try:
            idx = self.dropdowns.index(triggering_dropdown)
            # Clear everything AFTER this index
            for i in range(idx + 1, len(self.dropdowns)):
                dd = self.dropdowns[i]
                # Clear text and values
                dd._var.set("") 
                dd._entry.delete(0, tk.END)
                dd._entry.insert(0, dd._placeholder)
                dd._entry.config(fg='gray')
                dd["values"] = []
                dd.set_color_mode('gray')
            
            # Reset labels if any
            self.username_label.config(text="Username: ")
            self.password_label.config(text="Password: ")
            self.session_label.config(text="Session: ")
            self.portal_url_label.config(text="Portal URL: ")
            self.proxy_label.config(text="Proxy: ")
        except (ValueError, AttributeError):
            pass


    def logout(self):
        """Logs out the user, resets UI, and clears login fields."""
        confirm = messagebox.askyesno("Logout", "Are you sure you want to log out?")
        if confirm:
            # Hide the client frame
            if hasattr(self, "client_frame"):
                self.client_frame.place_forget()

            # Unhide the login frame
            if hasattr(self, "login_frame"):
                self.login_frame.place(relx=0.5, rely=0.5, anchor="center")
            
            # Restore placeholders for email and password fields
            if hasattr(self, "email_entry"):
                self.email_entry.delete(0, tk.END)  # Clear the field
                self.email_entry.insert(0, "Enter your email")  # Restore placeholder
            
            if hasattr(self, "password_entry"):
                self.password_entry.delete(0, tk.END)  # Clear the field
                self.password_entry.insert(0, "Enter your password")  # Restore placeholder
            
            # Hide the logout button if present
            if hasattr(self, "logout_button_top") and self.logout_button_top.winfo_exists():
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

    def bind_dropdown_keyboard_sort(self, container, values_list, default_text="Select", on_return_handler=None):
        """Adds live search filtration to custom Entry+Listbox dropdown."""
        sorted_values = sorted([str(v) for v in values_list])
        container._all_values = sorted_values
        
        # Check if there's an existing Return binding to preserve it
        existing_return = None
        # We can't easily get the existing handler, so we'll use add='+' later
        # and ensure on_return handles navigation if popup is closed.
        
        def on_keyrelease(event):
            # Ignore special keys
            if event.keysym in ("Down", "Up", "Return", "Escape", "Tab", "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R"):
                return
            
            # If the dropdown is blue, it means it's being "altered". Reset it to gray.
            if container.cget('bg') == '#1877F2':
                container.set_color_mode('gray')

            value = container.get()
            
            # Skip if placeholder
            if value == container._placeholder or value == "":
                container._popup.withdraw()
                return
            
            # Filter data - Case-insensitive and smarter sorting
            current_values = container._all_values
            lower_val = value.lower()
            
            # Use starts-with first, then contains, all case-insensitive
            starts_with = [item for item in current_values if item.lower().startswith(lower_val)]
            contains = [item for item in current_values if lower_val in item.lower() and item not in starts_with]
            filtered_data = starts_with + contains
            
            # If no matches, don't show stale results
            if not filtered_data:
                 container._popup.withdraw()
                 return
                 
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
                
                # Trigger color update
                self.update_dropdown_colors(container)

                if container._callback:
                    container._callback(event)
                return "break"
            
            # If popup is not mapped, trigger the next action
            if on_return_handler:
                if callable(on_return_handler):
                    on_return_handler(event)
                elif hasattr(on_return_handler, 'focus_set'):
                    on_return_handler.focus_set()
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
        
        def on_keypress(event):
            # If the dropdown is blue, immediately turn it back to gray
            if container.cget('bg') == '#1877F2':
                container.set_color_mode('gray')
                # SELECTION LOCK: Trigger downstream clear
                self.reset_downstream(container)

        # Remove add='+' to prevent pileup on re-binding
        container.bind('<Key>', on_keypress) 
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
            self.bind_dropdown_keyboard_sort(self.main_client_dropdown, values_list, "Select Main Client", on_return_handler=self.sub_client_dropdown)


    def on_main_client_select(self, event):
        """Handle main client selection and fetch sub-clients."""
        selected_name = self.main_client_var.get()
        
        # Reset dependent dropdowns and data
        self.sub_client_var.set("Select Subclient")
        self.sub_client_dropdown["values"] = []
        self.sub_client_dropdown.set_color_mode('gray')
        self.portal_var.set("Select Portal")
        self.portal_dropdown["values"] = []
        self.portal_dropdown.set_color_mode('gray')
        self.accounts = [] 
        self.account_var.set("Select Account")
        self.account_dropdown["values"] = []
        self.account_dropdown.set_color_mode('gray')

        # Reset labels
        self.username_label.config(text="Username: ")
        self.password_label.config(text="Password: ")
        self.session_label.config(text="Session: ")
        self.portal_url_label.config(text="Portal URL: ")
        self.proxy_label.config(text="Proxy: ")

        # Load sub-clients for selected main client
        selected_name = self.main_client_var.get()
        selected_client = next(
            (c for c in self.client_data["main_clients"] if c["client_name"] == selected_name), 
            None
        )
        # Reset IDs
        self.selected_sub_client_id = None
        self.selected_portal_id = None
        self.selected_portal_url = None
        self.selected_portal_key = None

        if selected_client:
            client_id = selected_client["id"]
            threading.Thread(target=self.load_sub_clients, args=(client_id, selected_name), daemon=True).start()


    def load_sub_clients(self, client_id, expected_main_client):
        """Fetch and populate sub-clients."""
        response = self.account_fetch_data(SUB_CLIENTS_API, {"mainClientId": client_id})
        
        # Validate that the main client selection hasn't changed while we were fetching
        if self.main_client_var.get() != expected_main_client:
            return

        if response and response.get("status_code") == 200 and response.get("content") and response.get("content").get("data"):
            sub_clients_data = response["content"]["data"]
            values_list = sorted([sc["client_name"] for sc in sub_clients_data])
            
            def update_ui():
                self.client_data["sub_clients"] = response
                self.sub_client_dropdown["values"] = values_list
                self.bind_dropdown_keyboard_sort(self.sub_client_dropdown, values_list,"Select Subclient", on_return_handler=self.portal_dropdown)
            
            self.after(0, update_ui)
        else:
            self.after(0, lambda: messagebox.showerror("Error", "Failed to load sub-clients or unexpected API response."))


    def on_sub_client_select(self, event):
        """Handle sub-client selection and store `sub_client_id` for later use."""
        sub_clients_data = self.client_data["sub_clients"]["content"]["data"]
        selected_name = self.sub_client_var.get()
        selected_sub_client = next((sc for sc in sub_clients_data if sc["client_name"] == selected_name), None)

        if selected_sub_client:
            self.selected_sub_client_id = selected_sub_client["sub_client_id"]
            # Reset dependent dropdowns and IDs
            self.portal_var.set("Select Portal")
            self.portal_dropdown["values"] = []
            self.portal_dropdown.set_color_mode('gray')
            self.account_dropdown["values"] = []
            self.account_var.set("Select Account")
            self.account_dropdown.set_color_mode('gray')
            
            self.selected_portal_id = None
            self.selected_portal_key = None
            self.selected_portal_url = None
            threading.Thread(target=self.load_portals, args=(self.selected_sub_client_id, selected_name), daemon=True).start()


    def load_portals(self, sub_client_id, expected_sub_client):
        """Fetch and populate portals."""
        response = self.account_fetch_data(PORTALS_API, {"client_id": sub_client_id})
        
        # Validate synchronization
        if self.sub_client_var.get() != expected_sub_client:
            return

        if response:
            values_list = sorted([p["portal_name"] for p in response["content"]["data"]])
            
            def update_ui():
                self.client_data["portals"] = response["content"]["data"]
                self.portal_dropdown["values"] = values_list
                self.bind_dropdown_keyboard_sort(self.portal_dropdown, values_list,"Select Portal", on_return_handler=self.account_dropdown)
            
            self.after(0, update_ui)


    def on_portal_select(self, event):
        """Handle portal selection and fetch accounts."""
        portals_data = self.client_data["portals"]
        selected_name = self.portal_var.get()
        selected_portal = next((p for p in portals_data if p["portal_name"] == selected_name), None)
        if selected_portal:
            self.selected_portal_id = selected_portal["portal_id"]
            self.selected_portal_url = selected_portal["portal_url"]
            self.selected_portal_key = selected_portal.get("portal_key")
            # Reset account dropdown
            self.account_var.set("Select Account")
            self.account_dropdown["values"] = []
            self.account_dropdown.set_color_mode('gray')
            
            threading.Thread(target=self.load_accounts, args=(self.selected_sub_client_id, self.selected_portal_id, selected_name), daemon=True).start()


    def load_accounts(self, sub_client_id, portal_id, expected_portal):
        """Fetch and populate accounts."""
        response = self.account_fetch_data(ACCOUNT_API, {"client_id": sub_client_id, "portal_id": portal_id})
        
        # Validate synchronization
        if self.portal_var.get() != expected_portal:
            return

        if response:
            values_list = sorted([str(acc["account_id"]) for acc in response["content"]["data"]])
            
            def update_ui():
                self.accounts = response["content"]["data"]
                self.account_dropdown["values"] = values_list
                self.bind_dropdown_keyboard_sort(self.account_dropdown, values_list,"Select Account", on_return_handler=self.confirm_selection)
            
            self.after(0, update_ui)


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

    
    def confirm_selection(self, event=None):
        """Confirm selection and trigger login with strict validation."""
        # 1. Check all filled
        if not (self.main_client_var.get() and self.sub_client_var.get() and self.portal_var.get() and self.account_var.get()):
            messagebox.showwarning("Incomplete", "Please select all details to proceed.")
            return

        # 2. Strict Validation: Ensure values exist in our data lists
        main_c = self.main_client_var.get()
        valid_main = any(c["client_name"] == main_c for c in self.client_data.get("main_clients", []))
        if not valid_main:
            messagebox.showwarning("Invalid Selection", f"'{main_c}' is not a valid Main Client.")
            return

        sub_c = self.sub_client_var.get()
        sub_clients_list = self.client_data.get("sub_clients", {}).get("content", {}).get("data", [])
        valid_sub = any(sc["client_name"] == sub_c for sc in sub_clients_list)
        if not valid_sub:
            messagebox.showwarning("Invalid Selection", f"'{sub_c}' is not a valid Sub Client.")
            return

        portal_v = self.portal_var.get()
        valid_portal = any(p["portal_name"] == portal_v for p in self.client_data.get("portals", []))
        if not valid_portal:
            messagebox.showwarning("Invalid Selection", f"'{portal_v}' is not a valid Portal.")
            return

        account_v = self.account_var.get()
        selected_account = next((acc for acc in self.accounts if str(acc["account_id"]) == account_v), None)
        if not selected_account:
            messagebox.showwarning("Invalid Selection", f"'{account_v}' is not a valid Account ID.")
            return

        # 3. Proceed to login
        self.login_to_client_portal(selected_account)


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
                selected_account["account_id"],
                self.selected_portal_key
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


