import logging
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from portal.Proteck import Proteck
from portal.RedBell import RedBell
from utility.file_util import resource_path
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
        self.driver = None  #Store Selenium WebDriver instance
        logging.basicConfig(level=logging.INFO)
    @staticmethod
    def portals(username, password, portal_url, portal_name,proxy):  # Added client_data parameter
        portal_name = portal_name.strip()
        if portal_name == 'Proteck':
            return Proteck(username, password, portal_url, portal_name,proxy)
        elif portal_name == 'RedBell':
            return RedBell(username, password, portal_url, portal_name,proxy)
        else:
            print("New portal")
            # return PortalLogin(username, password, portal_url, portal_name,proxy) #or create a default portal.

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
