from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from tkinter import messagebox
import time
from selenium.common.exceptions import TimeoutException, NoSuchElementException
# from utility.helper import log_login_status,initialize_driver
from selenium.webdriver.chrome.service import Service
from portal.RedBell import RedBell
from portal.Proteck import Proteck

from utility.helper import handle_login_status
class PortalLogin:
    def __init__(self, client_data):
        self.client_data = client_data
        self.driver = None  #Store Selenium WebDriver instance
        logging.basicConfig(level=logging.INFO)

    def portals(username, password, portal_url, portal_name,proxy):  # Added client_data parameter
        portal_name = portal_name.strip()
        if portal_name == 'Proteck':
            return Proteck(username, password, portal_url, portal_name,proxy)
        elif portal_name == 'RedBell':
            return RedBell(username, password, portal_url, portal_name,proxy)
        else:
            return PortalLogin(username, password, portal_url, portal_name,proxy) #or create a default portal.

    def login_to_portal(self, username, password, portal_url, portal_name,proxy):
        """Login to the portal with the selected account details."""
        portal_name = portal_name.strip()
        if portal_name == 'Proteck':
            portal_name_instance = Proteck(username, password, portal_url, portal_name,proxy)  # Create Proteck instance
            portal_name_instance.login_to_portal(username, password, portal_url, portal_name,proxy)  # Perform Proteck login
        elif portal_name == 'RedBell':
            portal_name_instance = RedBell(username, password, portal_url, portal_name,proxy)  # Create Proteck instance
            portal_name_instance.login_to_portal(username, password, portal_url, portal_name,proxy)
            session = portal_name_instance.login_to_portal(username, password, portal_url, portal_name, proxy)
            if type(session)==str:
                if "Login error" in session or 'Login issue' in session:  # Perform Proteck login
                    print("Login error")
        else:
            # Add default login logic here
            print(f"Default login called: {username}, {portal_name}")
