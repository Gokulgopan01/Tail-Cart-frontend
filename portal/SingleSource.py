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

from utils.helper import get_cookie_from_api, handle_login_status
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
    def login_to_portal(self, username, password, portal_url, portal_name, proxy,session):
        try:
            options = Options()
            options.add_argument("--start-maximized")
            options.add_argument("--disable-extensions")
            if proxy:
                logging.info(f"Using proxy: {proxy}")
                options.add_argument(f'--proxy-server={proxy}')

            self.driver = webdriver.Chrome(options=options)

            # API call to get cookie
            api_url = os.getenv("AUTHENTICATOR_API_URL")
            headers = {'Content-Type': os.getenv("API_HEADERS_CONTENT_TYPE")}
            api_response = get_cookie_from_api(self.username, portal="rrr", proxy=self.proxy)
            if not api_response:
                self.login_status = "API response error"
                handle_login_status("API_FAILED", self.username, ["VendorPortal/Index"], self.portal_name)
                return "Login error", self.driver
            #portal_url="https://valuationops.homegenius.com/VendorPortal"
            if api_response.get("status") == "success":
                redbell_cookie = api_response["cookies"].get(".ASPXAUTH")
                if redbell_cookie:
                    self.driver.get(portal_url) # Navigate to the site before adding cookie.
                    self.driver.add_cookie({'name': '.ASPXAUTH', 'value': redbell_cookie})
                    self.driver.get(f"{portal_url}/Index") # Navigate to index after cookie.
                    
                    # Wait for the page to load.
                    # Wait for login success by checking page title
                    #WebDriverWait(self.driver, 120).until(EC.presence_of_element_located((By.ID, "Partner portal")))


                    title = self.driver.current_url
                    login_check_keyword=["VendorPortal/Index","DailyUpdates"]

                    handle_login_status(title, username, login_check_keyword,portal_name)
                     
                    return self.driver  # Return the driver instance
                else:
                    logging.error("Cookie '.ASPXAUTH' not found in API response.")
                    title="MFA FAILED"
                    login_check_keyword=["False"]
                    handle_login_status(title, username, login_check_keyword,portal_name)
                    #return False
                   
            else:
                logging.error(f"API call failed: {api_response.get('status')}")
                title="MFA FAILED"
                login_check_keyword=["False"]
                handle_login_status(title, username, login_check_keyword,portal_name)
                #return False

        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {e}")
            title="MFA FAILED"
            login_check_keyword=["False"]
            handle_login_status(title, username, login_check_keyword,portal_name)
            #return False
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON response: {e}")
            title="MFA FAILED"
            login_check_keyword=["False"]
            handle_login_status(title, username, login_check_keyword,portal_name)
            #return False
        except Exception as e:
            logging.exception(f"An error occurred: {e}")
            title="MFA FAILED"
            login_check_keyword=["False"]
            handle_login_status(title, username, login_check_keyword,portal_name)
            #return False
        # finally:
        #     if self.driver:
        #         self.driver.quit()
    # def close_browser(self):
    #     if self.driver:
    #         self.driver.quit()
