import logging
import sys
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from portal import (
    Ascribe, ca, xome, rrreview, RedBell, AVM, Proteck, LSI, RealtyPilot, 
    AMO, ClearCapital, AppliedValuation, EstreetNew, BidOnHomes, 
    GroundWorks, InspectionPort, ValuationConnect, SWBC, Solidify, 
    SolidifyAppraiser, ClassValuation, Omnia, Valligent, 
    ClassValuationNew, SingleSource
)


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
from config import env
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


class PortalLoginScreen(tk.Frame):

    def __init__(self, client_data):
        self.client_data = client_data
        #self.driver = None  #Store Selenium WebDriver instance
        logging.basicConfig(level=logging.INFO)
   

    @staticmethod
    

    def portals(username, password, portal_url, portal_name, proxy, session,account_id,portal_key):
        portal_name = portal_key.strip()
        

        # # Load portal class map from JSON
        # with open('json/portal_map.json', 'r') as f:
        #     portal_class_map = json.load(f)
        # Handle PyInstaller temporary folder
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        json_path = os.path.join(base_dir, 'json', 'portal_map.json')

        with open(json_path, 'r') as f:
            portal_class_map = json.load(f)

        class_name = portal_class_map.get(portal_name)

        if not class_name:
            print(f"[!] Unsupported portal: {portal_name}")
            return None

        # Get class from globals() (assuming class is already imported in scope)
        portal_class = globals().get(class_name)

        if portal_class:
            try:
                return portal_class(username, password, portal_url, portal_name, proxy, session, account_id, portal_key)
            except TypeError:
                # Fallback for portals not yet refactored to accept new parameters
                return portal_class(username, password, portal_url, portal_name, proxy, session, account_id, portal_key)
        else:
            print(f"[!] Class {class_name} not found in global scope.")
            return None


          

    def login_to_portals(self, username, password, portal_url, portal_name, proxy=None, session=None, account_id=None, portal_key=None):
        """Generic login dispatcher that calls appropriate portal logic."""

        from screens.portal_login_screen import PortalLoginScreen  # Import inside if circular import
        print("portalinstruction")
        portal_instance = PortalLoginScreen.portals(
            username=username,
            password=password,
            portal_url=portal_url,
            portal_name=portal_name,
            proxy=proxy,
            session=session,
            account_id=account_id,
            portal_key=portal_key
        )

        if portal_instance:
            portal_instance.login_to_portal()
            return portal_instance.session, portal_instance.driver
        else:
            return None, None
        


        
