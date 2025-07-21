import time
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import logging
from dotenv import load_dotenv
import requests
import json
import os
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
# --- Redbell Class (Assuming portal.Proteck.py is renamed to portal_login.py and Redbell is implemented there) ---WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Dashboard')]")) #Replace with unique element.
                   

import logging
import requests
import json
import os
from selenium.webdriver.chrome.options import Options
from config import env
from utils.helper import get_cookie_from_api, handle_login_status, setup_driver, update_client_account_status, update_order_status
# Load environment variables from the .env file
load_dotenv()
class SS:
    def __init__(self,username, password, portal_url, portal_name, proxy,session):
        self.username = username
        self.password = password
        self.portal_url = portal_url
        self.portal_name = portal_name
        self.proxy = proxy
        self.session = session
        self.driver = None  # Initialize driver to None
        logging.basicConfig(level=logging.INFO)
    def login_to_portal(self):
        try:
            # Step 1: Setup Selenium WebDriver
            setup_driver(self)

            # Step 2: Prepare Authenticator API Request
            api_url = env.AUTHENTICATOR_API_URL
            headers = {'Content-Type': env.API_HEADERS_CONTENT_TYPE}
            payload = json.dumps({"username": self.username})

            response = requests.post(api_url, headers=headers, data=payload)
            response.raise_for_status()
            api_response = response.json()

            # Step 3: Validate API Response and Extract Cookie
            if api_response.get("status") != "success":
                logging.error(f"API response status not successful: {api_response.get('status')}")
                raise Exception("Authentication API returned failure")

            auth_cookie = api_response.get("cookies", {}).get(".ASPXAUTH")
            if not auth_cookie:
                logging.error("Missing '.ASPXAUTH' cookie in API response.")
                raise Exception("Missing cookie from API response")

            # Step 4: Inject Cookie into Browser and Navigate
            self.driver.get(self.portal_url)
            self.driver.add_cookie({'name': '.ASPXAUTH', 'value': auth_cookie})
            self.driver.get(f"{self.portal_url}/Index")

            # Step 5: Check Login Status from URL
            current_url = self.driver.current_url
            login_check_keywords = ["VendorPortal/Index", "DailyUpdates"]

           

            # Step 7: Check Entry Type (SmartEntry or Regular)
            # entry_type, _ = params_check()
            # if entry_type == "SmartEntry":
            #     orders, session = self.fetch_data(self.session)
            #     self.redbell_formopen(
            #         orders=orders,
            #         session=session,
            #         merged_json=None,
            #         order_details=self.order_details,
            #         order_id=self.order_id
            #     )
            #     logging.info("RedBell form open completed.")
            # else:
            handle_login_status(current_url, self.username, login_check_keywords, self.portal_name)

            return self.driver, self.session

        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            logging.error(f"API communication error: {e}")
        except Exception as e:
            logging.exception("Login to portal failed.")

        # Final Fallback: Update status and report failure
        title = "MFA FAILED"
        login_check_keywords = ["False"]
        update_order_status(self.order_id, "In Progress", "Entry", "Failed")
        #update_client_account_status(self.order_id)
        handle_login_status(title, self.username, login_check_keywords, self.portal_name)
        return None, None
                #return False
            # finally:
            #     if self.driver:
            #         self.driver.quit()
        # def close_browser(self):
        #     if self.driver:
        #         self.driver.quit()
