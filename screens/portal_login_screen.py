import logging
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from portal.Ascribe import Ascribe
from portal.ca import ca
from portal.xome import xome
from portal.rrreview import rrreview
from portal.RedBell import RedBell
from portal.AVM import AVM
from portal.Proteck import Proteck
from portal.LSI import LSI

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
import json

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


class PortalLoginScreen(tk.Frame):

    def __init__(self, client_data):
        self.client_data = client_data
        #self.driver = None  #Store Selenium WebDriver instance
        logging.basicConfig(level=logging.INFO)
    # @staticmethod
    # def portals(username, password, portal_url, portal_name,proxy,session):  # Added client_data parameter
    #     portal_name = portal_name.strip()
    #     if portal_name == 'Proteck':
    #         return Proteck(username, password, portal_url, portal_name,proxy,session)
    #     elif portal_name == 'RedBell':
    #         return RedBell(username, password, portal_url, portal_name,proxy,session)
    #     elif portal_name == 'AVM':
    #         return AVM(username, password, portal_url, portal_name,proxy,session)
    #         # return PortalLogin(username, password, portal_url, portal_name,proxy) #or create a default portal.
    #     elif portal_name == 'rrreview':
    #         return rrreview(username, password, portal_url, portal_name,proxy,session)  
    #     elif portal_name == 'xome':
    #         return xome(username, password, portal_url, portal_name,proxy,session) 
    #     elif portal_name == 'ca':
    #         return ca(username, password, portal_url, portal_name,proxy,session) 
    #     elif portal_name == 'Ascribe':
    #         return Ascribe(username, password, portal_url, portal_name,proxy,session) 
    #     elif portal_name == 'LSI':
    #         return LSI(username, password, portal_url, portal_name,proxy,session) 
    #     else:
    #         print("New portal")  

    @staticmethod
    

    def portals(username, password, portal_url, portal_name, proxy, session):
        portal_name = portal_name.strip()

        # Load portal class map from JSON
        with open('json/portal_map.json', 'r') as f:
            portal_class_map = json.load(f)

        class_name = portal_class_map.get(portal_name)

        if not class_name:
            print(f"[!] Unsupported portal: {portal_name}")
            return None

        # Get class from globals() (assuming class is already imported in scope)
        portal_class = globals().get(class_name)

        if portal_class:
            return portal_class(username, password, portal_url, portal_name, proxy, session)
        else:
            print(f"[!] Class {class_name} not found in global scope.")
            return None


    # def login_to_portal(self, username, password, portal_url, portal_name,proxy=None ,session=None):
    #     """Login to the portal with the selected account details."""
     
    #     portal_name = portal_name.strip()
    #     if portal_name == 'Proteck':
    #         portal_name_instance = Proteck(username, password, portal_url, portal_name,proxy,session)  # Create Proteck instance
    #         portal_name_instance.login_to_portal(username, password, portal_url, portal_name,proxy,session)  # Perform Proteck login
    #         return session, portal_name_instance.driver  # Return orders, session, and driver after login
    #     elif portal_name == 'RedBell':
    #         portal_name_instance = RedBell(username, password, portal_url, portal_name,proxy,session) 
    #         portal_name_instance.login_to_portal()
    #     elif portal_name == 'AVM':
    #         portal_name_instance = AVM(username, password, portal_url, portal_name,proxy,session)  # Create Proteck instance
    #         portal_name_instance.login_to_portal()  # Perform Proteck login
    #         return session, portal_name_instance.driver  # Return orders, session, and driver after login
    #     elif portal_name == 'rrreview':
    #         portal_name_instance = rrreview(username, password, portal_url, portal_name,proxy,session)  # Create Proteck instance
    #         portal_name_instance.login_to_portal()  # Perform Proteck login
    #         return session, portal_name_instance.driver  # Return orders, session, and driver after login
    #     elif portal_name == 'xome':
    #         portal_name_instance = xome(username, password, portal_url, portal_name,proxy,session)  # Create Proteck instance
    #         portal_name_instance.login_to_portal()  # Perform Proteck login
    #         return session, portal_name_instance.driver  # Return orders, session, and driver after login
    #     elif portal_name == 'ca':
    #         portal_name_instance = ca(username, password, portal_url, portal_name,proxy,session)  # Create Proteck instance
    #         portal_name_instance.login_to_portal()  # Perform Proteck login
    #         return session, portal_name_instance.driver  # Return orders, session, and driver after login
    #     elif portal_name == 'Ascribe':
    #         portal_name_instance = Ascribe(username, password, portal_url, portal_name,proxy,session)  # Create Proteck instance
    #         portal_name_instance.login_to_portal()  
    #         return session, portal_name_instance.driver 
    #     elif portal_name == 'LSI':
    #         portal_name_instance = LSI(username, password, portal_url, portal_name,proxy,session)  # Create Proteck instance
    #         portal_name_instance.login_to_portal()  
    #         return session, portal_name_instance.driver 
    #         # if type(session)==str:
    #         #     if "Login error" in session or 'Login issue' in session:  # Perform Proteck login
    #         #         print("Login error")
    #     else:
    #         # Add default login logic here
    #         print(f"Default login called: {username}, {portal_name}")
    #     #self.after(0, self.perform_login)       
    # 
    def login_to_portal(self, username, password, portal_url, portal_name, proxy=None, session=None):
        """Generic login dispatcher that calls appropriate portal logic."""

        portal_instance = self.portals(username, password, portal_url, portal_name, proxy, session)

        if portal_instance:
            portal_instance.login_to_portal()
            return portal_instance.session, portal_instance.driver
        else:
            return None, None
    
