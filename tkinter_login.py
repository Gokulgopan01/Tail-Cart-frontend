# import tkinter as tk

# def open_new_window():
#     new_window = tk.Toplevel(root)  # Creates a new top-level window
#     new_window.title("New Window")
#     tk.Label(new_window, text="This is a new window").pack()

# # Main window
# root = tk.Tk()
# root.title("Main Window")

# # Button to open a new window
# tk.Button(root, text="ENTRY WINDOW", command=open_new_window).pack()

# root.mainloop()


'''import tkinter as tk

def open_second_window():
    second_window = tk.Tk()  # Creates a completely independent window
    second_window.title("Second Window")
    tk.Label(second_window, text="This is a second window").pack()

# Main window
root = tk.Tk()
root.title("Main Window")

tk.Button(root, text="Open Another Window", command=open_second_window).pack()

root.mainloop()'''



'''import tkinter as tk
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def open_and_fill_forms():
    # Set up the Selenium WebDriver (Ensure you have the correct path for your WebDriver)
    driver = webdriver.Chrome()

    # URLs to open
    urls = [
        "https://www.google.com",
        "https://www.google.com",
        "https://www.google.com"
    ]

    search_queries = ["Python programming", "Tkinter tutorial", "Selenium automation"]

    # Open first tab
    driver.get(urls[0])
    search_box = driver.find_element("name", "q")  # Locate Google search box
    search_box.send_keys(search_queries[0])
    search_box.send_keys(Keys.RETURN)  # Press Enter

    # Open new tabs and fill forms
    for i in range(1, len(urls)):
        driver.execute_script(f"window.open('{urls[i]}', '_blank');")
        time.sleep(2)  # Give time for tab to open
        driver.switch_to.window(driver.window_handles[i])  # Switch to new tab
        search_box = driver.find_element("name", "q")
        search_box.send_keys(search_queries[i])
        search_box.send_keys(Keys.RETURN)

def run_script():
    open_and_fill_forms()

# Create Tkinter window
root = tk.Tk()
root.title("Open Multiple Tabs & Fill Forms")

# Button to start Selenium automation
btn = tk.Button(root, text="Open Tabs & Fill Forms", command=run_script)
btn.pack(pady=10)

root.mainloop()'''




##########################
'''import os
import time
import logging
import requests
import sys
import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Function to perform login
def login():
    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if not username or not password:
        
        messagebox.showerror("Input Error", "Please enter both username and password!")
        return

    try:
        status_label.config(text="Logging in...", fg="blue")
        root.update_idletasks()

        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-extensions")

        # Set up WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.delete_all_cookies()

        # Open login page
        driver.get("https://www.protk.com/ProTeck.Iam.Web/Account/Login")
        wait = WebDriverWait(driver, 15)

        # Find username and password fields
        user_field = wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id='UserNameOrEmail']")))
        pass_field = wait.until(EC.visibility_of_element_located((By.XPATH, "//*[@id='Password']")))

        user_field.send_keys(username)
        time.sleep(1)
        pass_field.send_keys(password)
        time.sleep(1)

        # Click login button
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit']")))
        login_button.click()
        time.sleep(3)

        # Check if login is successful
        current_url = driver.current_url
        if 'workqueue/All/All' in current_url:
            status_label.config(text="Login Successful!", fg="green")
            messagebox.showinfo("Success", "Login Successful!")
        else:
            status_label.config(text="Login Failed!", fg="red")
            messagebox.showerror("Error", "Invalid username or password!")

    except Exception as e:
        status_label.config(text="Login Error!", fg="red")
        messagebox.showerror("Error", f"Login failed: {str(e)}")

# Creating the Tkinter Window
root = tk.Tk()
root.title("Automated Login")
root.geometry("400x250")

# Username Label & Entry
tk.Label(root, text="Username:").pack(pady=5)
username_entry = tk.Entry(root, width=30)
username_entry.pack()

# Password Label & Entry
tk.Label(root, text="Password:").pack(pady=5)
password_entry = tk.Entry(root, width=30, show="*")
password_entry.pack()

# Login Button
login_button = tk.Button(root, text="Login", command=login)
login_button.pack(pady=10)

# Status Label
status_label = tk.Label(root, text="", fg="black")
status_label.pack()

# Run Tkinter main loop
root.mainloop()'''
#################################



import tkinter as tk
from tkinter import messagebox
import requests

''''def login():
    email = email_entry.get()
    password = password_entry.get()
    url = "http://192.168.3.48:8002/hybrid/api/v1/auth/signin"
    
    payload = {"email": email, "password": password}
    try:
        response = requests.post(url, json=payload)
        print(response.text)
        if response.status_code == 200:
            data = response.json()
            if data["status_code"] == 200 and data["content"]["data"]["success"]:
                username = data["content"]["data"]["username"]
                messagebox.showinfo("Login Successful", f"Welcome {username}")
            else:
                messagebox.showerror("Error", "Invalid credentials")
        else:
            messagebox.showerror("Error", "Invalid email or password")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Request failed: {e}")'''

'''def login():
    email = email_entry.get()
    password = password_entry.get()
    url = "http://192.168.3.48:8002/hybrid/api/v1/auth/signin"
    
    payload = {"email": email, "password": password}
    try:
        response = requests.post(url, json=payload)
        
        # Debugging: Print response details
        print("Status Code:", response.status_code)
        print("Response Headers:", response.headers)
        print("Response Text:", response.text)

        if response.status_code == 200:
            try:
                data = response.json()
                print("Parsed JSON:", data)  # Debugging line
                
                if data.get("status_code") == 200 and data.get("content", {}).get("data", {}).get("success"):
                    username = data["content"]["data"]["username"]
                    messagebox.showinfo("Login Successful", f"Welcome {username}")
                else:
                    messagebox.showerror("Error", "Invalid credentials")
            except Exception as e:
                messagebox.showerror("Error", f"JSON Parsing Error: {e}")
        else:
            messagebox.showerror("Error", "Invalid email or password")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Request failed: {e}")


# Create main application window
root = tk.Tk()
root.title("API Login")
root.geometry("300x200")

tk.Label(root, text="Email:").pack(pady=5)
email_entry = tk.Entry(root)
email_entry.pack(pady=5)

tk.Label(root, text="Password:").pack(pady=5)
password_entry = tk.Entry(root, show="*")
password_entry.pack(pady=5)

tk.Button(root, text="Login", command=login).pack(pady=10)

root.mainloop()'''


# import tkinter as tk
# from tkinter import messagebox
# import requests
# from tkinter import ttk

# def toggle_password():
#     if password_entry.cget('show') == '*':
#         password_entry.config(show='')
#         show_password_btn.config(text='🙈')
#     else:
#         password_entry.config(show='*')
#         show_password_btn.config(text='👁')

# def reset_password():
#     messagebox.showinfo("Forgot Password", "A password reset link has been sent to your email.")

# def login():
#     email = email_entry.get()
#     password = password_entry.get()
#     url = "http://192.168.3.48:8002/hybrid/api/v1/auth/signin"
    
#     payload = {"email": email, "password": password}
#     try:
#         response = requests.post(url, json=payload)
#         print("Status Code:", response.status_code)
#         print("Response Headers:", response.headers)
#         print("Response Text:", response.text)

#         if response.status_code == 200:
#             try:
#                 data = response.json()
#                 print("Parsed JSON:", data)
                
#                 if data.get("status_code") == 200 and data.get("content", {}).get("data", {}).get("success"):
#                     username = data["content"]["data"]["username"]
#                     messagebox.showinfo("Login Successful", f"Welcome {username}")
#                 else:
#                     messagebox.showerror("Error", "Invalid credentials")
#             except Exception as e:
#                 messagebox.showerror("Error", f"JSON Parsing Error: {e}")
#         else:
#             messagebox.showerror("Error", "Invalid email or password")
#     except requests.exceptions.RequestException as e:
#         messagebox.showerror("Error", f"Request failed: {e}")

# # Create main application window
# root = tk.Tk()
# root.title("Login")
# root.geometry("400x500")
# root.configure(bg='white')

# # Branding & Heading
# tk.Label(root, text="ECESIS", font=("Arial", 14, "bold"), bg='white').pack(pady=10)
# tk.Label(root, text="HYBRID BPO", font=("Arial", 16, "bold"), bg='white', fg='black', justify='center').pack(pady=5)
# tk.Label(root, text="Welcome back! Please login to your account to continue", font=("Arial", 10), bg='white', fg='#666').pack(pady=5)

# frame = tk.Frame(root, bg='white', padx=20, pady=20)
# frame.pack(pady=10)

# # Email Field
# tk.Label(frame, text="Email Address", bg='white', font=("Arial", 10), anchor='w').pack(pady=2, fill='x')
# email_entry = tk.Entry(frame, font=("Arial", 12), width=35, relief=tk.GROOVE, bd=2)
# email_entry.pack(pady=5, ipadx=5, ipady=5)

# # Password Field
# tk.Label(frame, text="Password", bg='white', font=("Arial", 10), anchor='w').pack(pady=2, fill='x')
# password_frame = tk.Frame(frame, bg='white')
# password_frame.pack(fill='x')

# password_entry = tk.Entry(password_frame, show="*", font=("Arial", 12), width=30, relief=tk.GROOVE, bd=2)
# password_entry.pack(side='left', padx=5, ipadx=5, ipady=5)

# show_password_btn = tk.Button(password_frame, text="👁", command=toggle_password, font=("Arial", 10), bg='white', bd=0)
# show_password_btn.pack(side='right', padx=5)

# # Remember Me & Forgot Password
# options_frame = tk.Frame(frame, bg='white')
# options_frame.pack(fill='x', pady=5)

# tk.Checkbutton(options_frame, text="Remember me", bg='white', font=("Arial", 10)).pack(side='left')
# tk.Button(options_frame, text="Forgot Password", command=reset_password, font=("Arial", 10), bg='white', fg='#007BFF', bd=0).pack(side='right')

# # Buttons
# button_frame = tk.Frame(frame, bg='white')
# button_frame.pack(fill='x', pady=10)

# tk.Button(button_frame, text="LOGIN", command=login, font=("Arial", 12, "bold"), bg='#007BFF', fg='white', width=15, height=2, relief=tk.FLAT).pack(side='left', padx=5)
# #tk.Button(button_frame, text="SIGNUP", font=("Arial", 12, "bold"), bg='white', fg='#007BFF', width=15, height=2, relief=tk.FLAT, bd=1).pack(side='right', padx=5)

# root.mainloop()
#########################


# import tkinter as tk
# from tkinter import messagebox, Canvas
# import requests

# def toggle_password():
#     if password_entry.cget('show') == '*':
#         password_entry.config(show='')
#         show_password_btn.config(text='🙈')
#     else:
#         password_entry.config(show='*')
#         show_password_btn.config(text='👁')

# def reset_password():
#     """Handle password reset logic"""
#     messagebox.showinfo("Forgot Password", "A password reset link has been sent to your email.")

# def login():
#     """Authenticate user via API"""
#     email = email_entry.get()
#     password = password_entry.get()
#     url = "http://192.168.3.48:8002/hybrid/api/v1/auth/signin"

#     payload = {"email": email, "password": password}
#     try:
#         response = requests.post(url, json=payload)
#         print("Status Code:", response.status_code)
#         print("Response:", response.text)

#         if response.status_code == 200:
#             try:
#                 data = response.json()
#                 if data.get("status_code") == 200 and data.get("content", {}).get("data", {}).get("success"):
#                     username = data["content"]["data"]["username"]
#                     messagebox.showinfo("Login Successful", f"Welcome {username}")
#                 else:
#                     messagebox.showerror("Error", "Invalid credentials")
#             except Exception as e:
#                 messagebox.showerror("Error", f"JSON Parsing Error: {e}")
#         else:
#             messagebox.showerror("Error", "Invalid email or password")
#     except requests.exceptions.RequestException as e:
#         messagebox.showerror("Error", f"Request failed: {e}")

# # Create main window
# root = tk.Tk()
# root.title("Login")
# root.geometry("400x500")
# root.configure(bg='white')

# # Branding & Title
# tk.Label(root, text="ECESIS", font=("Arial", 14, "bold"), bg='white').pack(pady=10)
# tk.Label(root, text="HYBRID BPO UI LOGIN", font=("Arial", 16, "bold"), bg='white', fg='black', justify='center').pack(pady=5)
# tk.Label(root, text="Welcome back! Please login to your account to continue", font=("Arial", 10), bg='white', fg='#666').pack(pady=5)

# frame = tk.Frame(root, bg='white', padx=20, pady=20)
# frame.pack(pady=10)

# # Email Field
# tk.Label(frame, text="Email Address", bg='white', font=("Arial", 10), anchor='w').pack(pady=2, fill='x')
# email_frame = tk.Frame(frame, bg='white')
# email_frame.pack(fill='x')

# email_entry = tk.Entry(email_frame, font=("Arial", 12), width=30, relief=tk.GROOVE, bd=2)
# email_entry.pack(side='left', padx=5, ipadx=5, ipady=5)

# # Password Field
# tk.Label(frame, text="Password", bg='white', font=("Arial", 10), anchor='w').pack(pady=2, fill='x')
# password_frame = tk.Frame(frame, bg='white')
# password_frame.pack(fill='x')

# password_entry = tk.Entry(password_frame, show="*", font=("Arial", 12), width=30, relief=tk.GROOVE, bd=2)
# password_entry.pack(side='left', padx=5, ipadx=5, ipady=5)

# show_password_btn = tk.Button(password_frame, text="👁", command=toggle_password, font=("Arial", 10), bg='white', bd=0)
# show_password_btn.pack(side='right', padx=5)

# # Remember Me & Forgot Password
# options_frame = tk.Frame(frame, bg='white')
# options_frame.pack(fill='x', pady=5)

# tk.Checkbutton(options_frame, text="Remember me", bg='white', font=("Arial", 10)).pack(side='left')
# tk.Button(options_frame, text="Forgot Password", command=reset_password, font=("Arial", 10), bg='white', fg='#007BFF', bd=0).pack(side='right')

# # Styled Login Button
# canvas = Canvas(frame, width=200, height=60, bg='white', highlightthickness=0)
# canvas.pack(pady=10)

# # Draw button shape (rounded rectangle)
# button_bg = canvas.create_oval(10, 10, 190, 50, fill="#007BFF", outline="#0056b3", width=3)

# # Add text inside the button
# button_text = canvas.create_text(100, 30, text="LOGIN", font=("Arial", 14, "bold"), fill="white")

# # Simulate click effect
# def on_click(event):
#     login()

# # Bind click event to the button
# canvas.tag_bind(button_bg, "<Button-1>", on_click)
# canvas.tag_bind(button_text, "<Button-1>", on_click)

# root.mainloop()
################################


#############################

import tkinter as tk
from tkinter import messagebox
import requests
from PIL import Image, ImageTk

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
    url = "http://192.168.3.48:8002/hybrid/api/v1/auth/signin"

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
tk.Label(root, text="HYBRID BPO UI LOGIN", font=("Arial", 16, "bold"), bg='white', fg='black', justify='center').pack(pady=5)
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


