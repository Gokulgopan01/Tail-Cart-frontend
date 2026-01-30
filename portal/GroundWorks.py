
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
                   

class GroundWorks:
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
            # Step 1: Setup WebDriver
            setup_driver(self)

            # Step 2: Navigate to Login Page
            self.driver.get(self.portal_url)
            logging.info(f"Navigated to {self.portal_url} for {self.username}")

            wait = WebDriverWait(self.driver, 20)

            # Step 3: Fill Username
            wait.until(EC.presence_of_element_located((By.NAME, "ctl00$ContentPlaceHolder1$txtLogin"))).send_keys(self.username)

            # Step 4: Fill Password
            wait.until(EC.presence_of_element_located((By.NAME, "ctl00$ContentPlaceHolder1$txtPassword"))).send_keys(self.password)

            # Step 5: Click Submit/Login
            wait.until(EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_btnsubmit"))).click()

            # Step 6: Post-login check
            wait.until(lambda d: d.current_url != self.portal_url)  # Wait for redirection

            current_url = self.driver.current_url
            logging.info(f"Current URL after login: {current_url}")

            login_check_keywords = ["Collaterals","DataCollectorDashboard"]
            handle_login_status(current_url, self.username, login_check_keywords, self.portal_name)

            return self.driver

        except Exception as e:
            self.login_status = f"Exception occurred: {e}"
            logging.exception("Exception during login")
            handle_login_status("EXCEPTION", self.username, ["Exception during login"], self.portal_name)
            #update_client_account_status(self.order_id)
            return "Login error", self.driver

