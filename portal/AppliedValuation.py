
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
                   

class AppliedValuation:
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

            # Optional sleep (can be replaced with WebDriverWait if needed)
            time.sleep(2)

            # Enter Username
            self.driver.find_element(By.ID, "txt_username").send_keys(self.username)
            time.sleep(2)

            # Enter Password
            self.driver.find_element(By.ID, "txt_password").send_keys(self.password)

            # Click Login Button
            self.driver.find_element(By.ID, "Button1").click()
            time.sleep(2)

            try:
                WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Click here to continue to Applied Valuation Services Business Manager"))).click()
                print("Successfully clicked the 'Click here to continue' link.")
            except Exception as e:
                print(f"no link to click : {e}")

            # Check URL after login
            current_url = self.driver.current_url
            logging.info(f"URL after login: {current_url}")

            login_check_keywords = ["vweb"]
            handle_login_status(current_url, self.username, login_check_keywords, self.portal_name)

            return self.driver

        except Exception as e:
            self.login_status = f"Exception occurred: {e}"
            logging.exception("Exception during login")
            handle_login_status("EXCEPTION", self.username, ["Exception during login"], self.portal_name)
            return "Login error", self.driver

