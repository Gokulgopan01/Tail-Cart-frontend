import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from selenium.webdriver.chrome.service import Service
import logging
from tkinter import messagebox
import sys
from urllib.parse import urlparse, parse_qs

def initialize_driver(self):
        """Initialize Selenium WebDriver."""
        try:
                chrome_options = Options()
                chrome_options.add_argument("--start-maximized") 
                chrome_options.add_argument("--disable-notifications")

                service = Service("chromedriver.exe") 
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                return self.driver
        except Exception as e:
                logging.error(f"Error initializing WebDriver: {e}")
                return None



def handle_login_status(login_title_or_url, username,log_check_value, portal_name):
    """Handle login success or failure based on title or URL."""
    # Check if login_title_or_url contains 'Partner Portal'
    if log_check_value not in login_title_or_url:
        # Log the login failure
        logging.error(f"Login failed for {username} on {portal_name} due to incorrect credentials or login error.")
        
        # Show error message to the user
        messagebox.showerror("Login Failed", "Invalid credentials or login error.")
        

    else:
        # Log the login success
        logging.info(f"Successfully logged in to {portal_name} with username {username}.")
        
        # Show success message to the user
        messagebox.showinfo("Login Successful", f"Successfully logged in to {portal_name}.")
        

def handle_exception(self, e):
        """Handle exceptions and log the error."""
        stack_trace = traceback.format_exc()
        if stack_trace:
            e = stack_trace
        self.update_report_data(None, str(e), 'UNABLE TO LOGIN')        


def params_check():
    
    if len(sys.argv) >= 2:
            url = sys.argv[1]  # Example: 'myapp://?arg1=mlsdownloader&arg2=order123'
            parsed_url = urlparse(url)
            args = parse_qs(parsed_url.query)
            arg1 = args.get('arg1', [None])[0]  # Get 'arg1' or None if not present
            arg2 = args.get('arg2', [None])[0]
            print(f"Args : {arg1}")   
            return arg1,arg2
    else:
          return None,None        
    

def on_closing(self):
    if messagebox.askokcancel("Quit", "Do you really want to exit?"):
        self.destroy()  # Close the application    