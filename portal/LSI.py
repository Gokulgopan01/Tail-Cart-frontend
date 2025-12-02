
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
                   

class LSI:
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
        """Login to the portal with username/password and check based on URL keyword."""
        try:
            setup_driver(self)

            self.driver.get(self.portal_url)
            logging.info(f"Navigated to {self.portal_url}...")
            # Wait and enter username
            WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.ID, "userName"))
            )
            self.driver.find_element(By.ID, "userName").clear()
            self.driver.find_element(By.ID, "userName").send_keys(self.username)
            self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

            # Wait and enter password
            WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.ID, "password"))
            )
            self.driver.find_element(By.ID, "password").clear()
            self.driver.find_element(By.ID, "password").send_keys(self.password)
            next_button = WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located((By.ID, "next")))
                        # Wait for the overlay to go invisible
            WebDriverWait(self.driver, 30).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, "temp-overlay"))
            )

            # Then click the button
            next_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, "next"))
            )
            next_button.click()


            time.sleep(10)  # Wait for final redirect
            current_url = self.driver.current_url
            logging.info(f"Final URL after login: {current_url}")

            login_check_keywords = ["CombinedSigninAndSignup"]
            handle_login_status(current_url, self.username, login_check_keywords, self.portal_name)

            return self.driver

        except Exception as e:
            self.login_status = f"Exception occurred: {e}"
            logging.exception("Exception during login")
            handle_login_status("EXCEPTION", self.username, ["Exception during login"], self.portal_name)
            #update_client_account_status(self.order_id)
            return "Login error", self.driver
