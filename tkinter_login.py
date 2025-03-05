import tkinter as tk
from tkinter import ttk, messagebox
import requests
from PIL import Image, ImageTk


#######################

# Sample Data
main_clients = [
    {"client_id": 1, "client_name": "John Doe"},
    {"client_id": 2, "client_name": "John Doe 2"}
]

sub_clients = [
    {"client_id": 1, "client_name": "John Doe"},
    {"client_id": 2, "client_name": "John Doe 2"}
]

portals = [
    {"portal_id": 1, "portal_name": "Redbell"},
    {"portal_id": 2, "portal_name": "Single Source"}
]

accounts = [
    {"account_id": 1, "portal_id": 1, "portal_name": "Redbell", "username": "john.doe", "password": "password1"},
    {"account_id": 3, "portal_id": 2, "portal_name": "Single Source", "username": "john.doe2", "password": "password2"}
]

# Function to update account dropdown based on portal selection
def update_accounts(event):
    selected_portal = portal_var.get()
    filtered_accounts = [a["username"] for a in accounts if a["portal_name"] == selected_portal]
    account_dropdown["values"] = filtered_accounts
    account_var.set("")

# Function to get credentials without displaying them
def get_credentials():
    selected_account = account_var.get()
    for account in accounts:
        if account["username"] == selected_account:
            return account["username"], account["password"]
    return None, None

# Function to login to the portal
def login_to_portal():
    username, password = get_credentials()
    if username and password:
        messagebox.showinfo("Portal Login", f"Logging into {portal_var.get()} with selected account.")
    else:
        messagebox.showerror("Error", "Please select a valid account.")

# Function to show the selection window after login
def open_selection_window():
    selection_window = tk.Toplevel(root)
    selection_window.title("Select Client & Account")
    selection_window.geometry("400x300")

    # Main Client Dropdown
    tk.Label(selection_window, text="Select Main Client:").pack(pady=5)
    main_client_var = tk.StringVar()
    main_client_dropdown = ttk.Combobox(selection_window, textvariable=main_client_var, values=[c["client_name"] for c in main_clients])
    main_client_dropdown.pack(pady=5)

    # Sub Client Dropdown
    tk.Label(selection_window, text="Select Sub Client:").pack(pady=5)
    sub_client_var = tk.StringVar()
    sub_client_dropdown = ttk.Combobox(selection_window, textvariable=sub_client_var, values=[c["client_name"] for c in sub_clients])
    sub_client_dropdown.pack(pady=5)

    # Portal Dropdown
    tk.Label(selection_window, text="Select Portal:").pack(pady=5)
    global portal_var
    portal_var = tk.StringVar()
    portal_dropdown = ttk.Combobox(selection_window, textvariable=portal_var, values=[p["portal_name"] for p in portals])
    portal_dropdown.pack(pady=5)
    portal_dropdown.bind("<<ComboboxSelected>>", update_accounts)

    # Account Dropdown
    tk.Label(selection_window, text="Select Account:").pack(pady=5)
    global account_var, account_dropdown
    account_var = tk.StringVar()
    account_dropdown = ttk.Combobox(selection_window, textvariable=account_var, values=[]) 
    account_dropdown.pack(pady=5)

    # Login to Portal Button
    tk.Button(selection_window, text="Login to Portal", font=("Arial", 12, "bold"), bg='#007BFF', fg='white', width=20, height=2, relief=tk.FLAT,
              command=login_to_portal).pack(pady=10)

def toggle_password():
    if password_entry.cget('show') == '*':
        password_entry.config(show='')
        show_password_btn.config(text='🙈')
    else:
        password_entry.config(show='*')
        show_password_btn.config(text='👁')

def reset_password():
    """Handle password reset logic"""
    messagebox.showinfo("Forgot Password", "A password reset link has been sent to your email.")

def login():
    """Authenticate user via API"""
    email = email_entry.get()
    password = password_entry.get()
    url = "http://192.168.3.48:8000/hybrid/api/v1/auth/signin"

    payload = {"email": email, "password": password}
    try:
        response = requests.post(url, json=payload)
        print("Status Code:", response.status_code)
        print("Response:", response.text)

        if response.status_code == 200:
            try:
                data = response.json()
                if data.get("status_code") == 200 and data.get("content", {}).get("data", {}).get("success"):
                    username = data["content"]["data"]["username"]
                    messagebox.showinfo("Login Successful", f"Welcome {username}")
                    open_selection_window()
                else:
                    messagebox.showerror("Error", "Invalid credentials")
            except Exception as e:
                messagebox.showerror("Error", f"JSON Parsing Error: {e}")
        else:
            messagebox.showerror("Error", "Invalid email or password")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Request failed: {e}")

# Create main window
root = tk.Tk()
root.title("Login")
root.geometry("400x500")
root.configure(bg='white')

# Branding & Title
tk.Label(root, text="ECESIS", font=("Arial", 14, "bold"), bg='white').pack(pady=10)
tk.Label(root, text="HYBRID BPO CLIENT LOGIN", font=("Arial", 16, "bold"), bg='white', fg='black', justify='center').pack(pady=5)
tk.Label(root, text="Welcome back! Please login to your account to continue", font=("Arial", 10), bg='white', fg='#666').pack(pady=5)

frame = tk.Frame(root, bg='white', padx=20, pady=20)
frame.pack(pady=10)

# Email Field
tk.Label(frame, text="Email Address", bg='white', font=("Arial", 10), anchor='w').pack(pady=2, fill='x')
email_frame = tk.Frame(frame, bg='white')
email_frame.pack(fill='x')

email_entry = tk.Entry(email_frame, font=("Arial", 12), width=30, relief=tk.GROOVE, bd=2)
email_entry.pack(side='left', padx=5, ipadx=5, ipady=5)

# Password Field
tk.Label(frame, text="Password", bg='white', font=("Arial", 10), anchor='w').pack(pady=2, fill='x')
password_frame = tk.Frame(frame, bg='white')
password_frame.pack(fill='x')

password_entry = tk.Entry(password_frame, show="*", font=("Arial", 12), width=30, relief=tk.GROOVE, bd=2)
password_entry.pack(side='left', padx=5, ipadx=5, ipady=5)

show_password_btn = tk.Button(password_frame, text="👁", command=toggle_password, font=("Arial", 10), bg='white', bd=0)
show_password_btn.pack(side='right', padx=5)

# Remember Me & Forgot Password
options_frame = tk.Frame(frame, bg='white')
options_frame.pack(fill='x', pady=5)

tk.Checkbutton(options_frame, text="Remember me", bg='white', font=("Arial", 10)).pack(side='left')
tk.Button(options_frame, text="Forgot Password", command=reset_password, font=("Arial", 10), bg='white', fg='#007BFF', bd=0).pack(side='right')

# Buttons
button_frame = tk.Frame(frame, bg='white')
button_frame.pack(fill='x', pady=10)


tk.Button(button_frame, text="LOGIN", command=login, font=("Arial", 12, "bold"), bg='#007BFF', fg='white', width=20, height=1, relief=tk.FLAT).pack(pady=10)

#tk.Button(button_frame, text="LOGIN", command=login, font=("Arial", 12, "bold"), bg='#007BFF', fg='white', width=15, height=2, relief=tk.FLAT).pack(side='left', padx=5)
#tk.Button(button_frame, text="SIGNUP", font=("Arial", 12, "bold"), bg='white', fg='#007BFF', width=15, height=2, relief=tk.FLAT, bd=1).pack(side='right', padx=5)

root.mainloop()


################


