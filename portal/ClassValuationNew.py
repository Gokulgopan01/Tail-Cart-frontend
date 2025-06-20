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

from form_filler.redbell_form_filler import RedBellFormFiller
from integrations.hybrid_bpo_api import HybridBPOApi
from utils.helper import clean_address, get_cookie_from_api, get_order_address_from_assigned_order, handle_login_status, params_check, setup_driver, update_client_account_status


# Load variables from .env file
load_dotenv()

# Retrieve API URLs from environment variables
ASSIGNEDORDERS_URL = os.getenv("ASSIGNEDORDERS_URL")  
                   

class ClassValuationNew:
    def __init__(self, username, password, portal_url, portal_name, proxy, session):
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

            # Step 2: Navigate to Login Page
            self.driver.get(self.portal_url)
            logging.info(f"Navigated to {self.portal_url} for {self.username}")

            wait = WebDriverWait(self.driver, 20)

            # Step 3: Enter Username
            wait.until(EC.presence_of_element_located((By.ID, "Username"))).send_keys(self.username)

            # Step 4: Enter Password
            wait.until(EC.presence_of_element_located((By.ID, "Password"))).send_keys(self.password)

            # Step 5: Click Terms Checkbox
            wait.until(EC.element_to_be_clickable((By.ID, "checkAcceptLoginTnC"))).click()

            # Step 6: Click Login Button
            wait.until(EC.element_to_be_clickable((By.ID, "submitLogin"))).click()

            current_title = self.driver.title
            logging.info(f"Page title after login: {current_title}")

            # Step 8: Verify Login
            login_check_keywords = ["Orders"]
            handle_login_status(current_title, self.username, login_check_keywords, self.portal_name)

            return self.driver

        except Exception as e:
            self.login_status = f"Exception occurred: {e}"
            logging.exception("Exception during login")
            handle_login_status("EXCEPTION", self.username, ["Exception during login"], self.portal_name)
            #update_client_account_status(self.order_id)
            return "Login error", self.driver