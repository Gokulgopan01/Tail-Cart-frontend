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



def handle_login_status(login_title_or_url, username,login_check_keywords, portal_name):
    """Handle login success or failure by checking the current URL."""

    # Check if the current URL contains any of the success indicators
    if any(keyword in login_title_or_url for keyword in login_check_keywords):
        logging.info(f"Successfully logged in to {portal_name} as {username}.")
        messagebox.showinfo("Login Successful", f"Successfully logged in to {portal_name} .")
    else:
        logging.error(f"Login failed for {username} on {portal_name}. Possible incorrect credentials or login issue.")
        messagebox.showerror("Login Failed", "Invalid credentials or login error for {portal_name}.")
        
        

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