
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
                   

class SolidifyAppraiser:
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

            # Step 2: Navigate to Portal URL
            self.driver.get(self.portal_url)
            logging.info(f"Navigated to {self.portal_url} for {self.username}")

            wait = WebDriverWait(self.driver, 20)

            # Step 3: Clear and Enter Username
            login_field = wait.until(EC.presence_of_element_located((By.NAME, "login")))
            login_field.clear()
            login_field.send_keys(self.username)

            # Step 4: Enter Password
            wait.until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(self.password)

            # Step 5: Click Submit Button
            wait.until(EC.element_to_be_clickable((By.NAME, "submit"))).click()

            # Step 6: Validate Login
            wait.until(EC.title_is_not("Login"))  # Wait until title changes
            current_title = self.driver.title
            logging.info(f"Page title after login: {current_title}")

            login_check_keywords = ["Login"]
            handle_login_status(current_title, self.username, login_check_keywords, self.portal_name)

            return self.driver

        except Exception as e:
            self.login_status = f"Login failed: {e}"
            logging.exception("Exception during login")
            handle_login_status("EXCEPTION", self.username, ["Login exception"], self.portal_name)
            return "Login error", self.driver