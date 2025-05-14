import time
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import logging
from dotenv import load_dotenv
import requests
import json
import os
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
# --- Redbell Class (Assuming portal.Proteck.py is renamed to portal_login.py and Redbell is implemented there) ---WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Dashboard')]")) #Replace with unique element.
                   

import logging
import requests
import json
import os
from selenium.webdriver.chrome.options import Options

from utils.helper import get_cookie_from_api, handle_login_status, setup_driver

import logging
import json
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import logging
import json
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Load environment variables from the .env file
load_dotenv()
class rrreview:
    def __init__(self, username, password, portal_url, portal_name, proxy, session):
        self.username = username
        self.password = password
        self.portal_url = portal_url
        self.portal_name = portal_name
        self.proxy = proxy
        self.driver = None
        self.login_status = "Not started"
        logging.basicConfig(level=logging.INFO)


    def login_to_portal(self):
        try:
    
            # Step 1: Setup WebDriver
            setup_driver(self)

            api_response = get_cookie_from_api(self.username, portal="rrr", proxy=self.proxy)
            if not api_response:
                self.login_status = "API response error"
                handle_login_status("API_FAILED", self.username, ["VendorPortal/Index"], self.portal_name)
                return "Login error", self.driver
            # Step 3: Inject session storage
            self.driver.get('https://www.rrreview.com/runtime.aa40cd539422f2485b46.js')
            time.sleep(1)

            for key, value in api_response.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        self.driver.execute_script(f"sessionStorage.setItem('{sub_key}', '{sub_value}');")
                else:
                    self.driver.execute_script(f"sessionStorage.setItem('{key}', '{value}');")

            # Step 4: Navigate to Active Orders
            self.driver.get('https://www.rrreview.com/#/baseauth/activeorders')
            time.sleep(5)

            # Step 5: Check if Login Successful
            current_url = self.driver.current_url
            if 'https://www.rrreview.com/#/baseauth/activeorders' in current_url:
                logging.info("Login successful")
                return "Login success", self.driver
            else:
                logging.error(f"Login failed. URL landed: {current_url}")
                return "Login error", self.driver

                # handle_login_status(current_url, self.username, success_keywords, self.portal_name)
                # return self.login_status, self.driver

        except Exception as e:
            self.login_status = f"Exception occurred: {e}"
            logging.exception("Exception during login")
            handle_login_status("EXCEPTION", self.username, ["activeorders"], self.portal_name)
            return "Login error", self.driver
