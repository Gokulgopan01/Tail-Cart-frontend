
import os
import time
import logging
import requests
import json
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from dotenv import load_dotenv


from integrations.hybrid_bpo_api import HybridBPOApi
from utils.helper import clean_address, get_cookie_from_api, get_order_address_from_assigned_order, handle_login_status, params_check, setup_driver, update_client_account_status


# Load variables from .env file
load_dotenv()

# Retrieve API URLs from environment variables
ASSIGNEDORDERS_URL = os.getenv("ASSIGNEDORDERS_URL")  
                   

class InspectionPort:
    def __init__(self, username, password, portal_url, portal_name, proxy, session,account_id, portal_key):
        self.username = username
        self.password = password
        self.portal_url = portal_url
        self.portal_name = portal_name
        self.proxy = proxy
        self.session = session
        self.driver = None
        self.order_details = None
        self.order_id = None
        self.portal_key = portal_key
        logging.basicConfig(level=logging.INFO)



    def login_to_portal(self):
        try:
            # Setup driver
            setup_driver(self)

            # Navigate to the portal URL
            self.driver.get(self.portal_url)
            logging.info(f"Opened portal URL: {self.portal_url}")

            wait = WebDriverWait(self.driver, 20)

            # Enter Username
            wait.until(EC.presence_of_element_located((By.ID, "Username"))).send_keys(self.username)
            
            # Enter Password
            wait.until(EC.presence_of_element_located((By.ID, "Password"))).send_keys(self.password)

            # Click login button
            wait.until(EC.element_to_be_clickable((By.ID, "logOnBtn"))).click()

            # # Wait for URL to change after login
            wait.until(lambda driver: driver.current_url != self.portal_url)
            current_url = self.driver.current_url
            logging.info(f"URL after login: {current_url}")

            # Check if login was successful
            login_check_keywords = ["Dashboard", "Profile"]
            handle_login_status(current_url, self.username, login_check_keywords, self.portal_name)

            return self.driver

        except Exception as e:
            self.login_status = f"Login failed: {e}"
            logging.exception("Exception during login")
            handle_login_status("EXCEPTION", self.username, ["Login exception"], self.portal_name)
            #update_client_account_status(self.order_id)
            return "Login error", self.driver
