
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
from utils.helper import clean_address, get_cookie_from_api, get_order_address_from_assigned_order, handle_login_status, params_check, setup_driver


# Load variables from .env file
load_dotenv()

# Retrieve API URLs from environment variables
ASSIGNEDORDERS_URL = os.getenv("ASSIGNEDORDERS_URL")  
                   

class ValuationConnect:
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
            # Initialize driver
            setup_driver(self)

            # Navigate to login page
            self.driver.get(self.portal_url)
            logging.info(f"Navigated to {self.portal_url} for {self.username}")

            wait = WebDriverWait(self.driver, 20)

            # Wait and enter Username
            wait.until(EC.presence_of_element_located((By.ID, "Username"))).send_keys(self.username)

            # Wait and enter Password
            wait.until(EC.presence_of_element_located((By.ID, "Password"))).send_keys(self.password)

            # Wait and click Terms & Conditions checkbox
            wait.until(EC.element_to_be_clickable((By.ID, "checkAcceptLoginTnC"))).click()

            # Click Submit/Login
            wait.until(EC.element_to_be_clickable((By.ID, "submitLogin"))).click()

            # # Wait until title changes after login
            # wait.until(lambda d: "Login" not in d.title)

            # Get the page title after login
            current_title = self.driver.title
            logging.info(f"Page title after login: {current_title}")

            # Check for successful login
            login_check_keywords = ["Orders"]
            handle_login_status(current_title, self.username, login_check_keywords, self.portal_name)

            return self.driver

        except Exception as e:
            self.login_status = f"Login failed: {e}"
            logging.exception("Exception during login")
            handle_login_status("EXCEPTION", self.username, ["Login exception"], self.portal_name)
            return "Login error", self.driver