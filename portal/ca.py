
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
                   

class ca:
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
            self.driver.get("https://vendors.ca-usa.com/Account/Login?ReturnUrl=%2FOrders%2FDashboard")

            # Step 2: Get API cookie
            api_response = get_cookie_from_api(self.username, portal="ca", proxy=self.proxy)
            if not api_response:
                self.login_status = "API response error"
                handle_login_status("API_FAILED", self.username, ["Orders/Dashboard"], self.portal_name)
                return "Login error", self.driver

            # Step 3: Inject cookies
            for name, value in api_response.get("cookies", {}).items():
                self.driver.add_cookie({"name": name, "value": value})
            self.driver.get("https://vendors.ca-usa.com/Orders/Dashboard")

            # Step 4: Confirm login
            time.sleep(3)
            current_url = self.driver.current_url
            if "Orders/Dashboard" in current_url:
                logging.info("Login successful")
                # Create session with same cookies
                session = requests.Session()
                for cookie in self.driver.get_cookies():
                    session.cookies.set(cookie['name'], cookie['value'])
                self.session = session
                handle_login_status(current_url, self.username, ["Orders/Dashboard"], self.portal_name)
            
                return session, self.driver
            else:
                try:
                    login_status = self.driver.find_element(By.XPATH, "//div[@id='validationSummary']/ul/li").text
                    if "Invalid login attempt." in login_status:
                        logging.warning("Login failed: Invalid credentials")
                        handle_login_status("INVALID_LOGIN", self.username, ["Orders/Dashboard"], self.portal_name)
                except Exception:
                    logging.error("Login failed and could not find login error message")

                return "Login error", self.driver

        except Exception as e:
            logging.exception("Exception during CA-USA login")
            handle_login_status("EXCEPTION", self.username, ["Orders/Dashboard"], self.portal_name)
            #update_client_account_status(self.order_id)
            return "Login error", self.driver
    