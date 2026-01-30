
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
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from integrations.hybrid_bpo_api import HybridBPOApi
from utils.helper import clean_address, get_cookie_from_api, get_order_address_from_assigned_order, handle_login_status, params_check, setup_driver, update_client_account_status


# Load variables from .env file
load_dotenv()

# Retrieve API URLs from environment variables
ASSIGNEDORDERS_URL = os.getenv("ASSIGNEDORDERS_URL")  
                   

class ClearCapital:
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
            self.driver.set_window_position(0, 0)
            self.driver.maximize_window()
            logging.info(f"Navigated to {self.portal_url} for {self.username}")

            # Step 3: Enter Username
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.NAME, "username_login"))
            ).send_keys(self.username)
            time.sleep(2)

            # Step 4: Click Submit after Username
            self.driver.find_element(By.ID, "submitButton").click()
            time.sleep(2)

            # Step 5: Enter Password
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.NAME, "password_login"))
            ).send_keys(self.password)
            time.sleep(2)

            # Step 6: Click Submit after Password
            self.driver.find_element(By.ID, "submitButton").click()
            time.sleep(4)

            try:
                agree_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="agree-link"]'))
                )
                agree_button.click()
                print("Clicked agree-link.")
            except (TimeoutException, NoSuchElementException):
                print("agree-link not found or not clickable. Continuing...")

            # Step 7: Check for Login Success
            current_url = self.driver.current_url
            logging.info(f"Current URL after login attempt: {current_url}")

            login_check_keywords = ["inprogress"]  # Add keywords as appropriate
            handle_login_status(current_url, self.username, login_check_keywords, self.portal_name)

            return self.driver
                    

        except Exception as e:
            self.login_status = f"Exception occurred: {e}"
            logging.exception("Exception during login")
            handle_login_status("EXCEPTION", self.username, ["Exception during login"], self.portal_name)
            #update_client_account_status(self.order_id)
            return "Login error", self.driver
