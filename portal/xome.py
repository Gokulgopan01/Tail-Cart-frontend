
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
from utils.helper import clean_address, get_cookie_from_api, get_order_address_from_assigned_order, handle_login_status, params_check, setup_driver


# Load variables from .env file
load_dotenv()

# Retrieve API URLs from environment variables
ASSIGNEDORDERS_URL = os.getenv("ASSIGNEDORDERS_URL")  
                   

class xome:
    def __init__(self, username, password, portal_url, portal_name, proxy, session,account_id):
        self.username = username
        self.password = password
        self.portal_url = portal_url
        self.portal_name = portal_name
        self.proxy = proxy
        self.session = session
        self.driver = None
        self.order_details = None
        self.order_id = None
        logging.basicConfig(level=logging.INFO)

    def login_to_portal(self):
        try:
            # Step 1: Setup WebDriver
            setup_driver(self)

            # Step 2: Call authentication API
            api_response = get_cookie_from_api(self.username, portal="xome", proxy=self.proxy)
            if not api_response:
                self.login_status = "API response error"
                handle_login_status("API_FAILED", self.username, ["vendor.voxturappraisal.com"], self.portal_name)
                return "Login error", self.driver

            # Step 3: Navigate to login page to prepare for cookie injection
            #self.driver.get("https://vendor.voxturappraisal.com/Account/Login")
            self.driver.get(self.portal_url)
            time.sleep(1)

            # Step 4: Inject cookie into browser
            cookie_name = f"v_pc_{self.username}"
            cookie_value = api_response.get("cookies", {}).get(cookie_name)

            if not cookie_value:
                logging.error(f"Cookie '{cookie_name}' not found in API response.")
                self.login_status = "Missing cookie"
                handle_login_status("COOKIE_FAILED", self.username, ["vendor.voxturappraisal.com"], self.portal_name)
                return "Login error", self.driver

            self.driver.add_cookie({"name": cookie_name, "value": cookie_value})
            self.driver.get("https://vendor.voxturappraisal.com/Account/Login")  # Refresh after cookie injection
            time.sleep(1)

            # Step 5: Fill in credentials manually (required by portal)
            self.driver.find_element(By.ID, "Login_Username").send_keys(self.username)
            self.driver.find_element(By.ID, "Login_Password").send_keys(self.password)
            self.driver.find_element(By.ID, "BtnLogin").click()
            time.sleep(2)

            # Step 6: Check if Login was successful
            current_url = self.driver.current_url
            if "vendor.voxturappraisal.com" in current_url:
                logging.info("Login successful for user: %s", self.username)
                self.login_status = "Login success"
                handle_login_status(current_url, self.username, ["vendor.voxturappraisal.com"], self.portal_name)
                return "Login success", self.driver
            else:
                logging.error(f"Login failed. Landed on: {current_url}")
                self.login_status = "Login failed"
                handle_login_status(current_url, self.username, ["Login failed"], self.portal_name)
                return "Login error", self.driver

        except Exception as e:
            self.login_status = f"Exception occurred: {e}"
            logging.exception("Exception during login")
            handle_login_status("EXCEPTION", self.username, ["Exception during login"], self.portal_name)
            return "Login error", self.driver
