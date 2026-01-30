import sys
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
                   
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import logging

from utils.helper import handle_login_status, setup_driver, update_client_account_status
# Load environment variables from the .env file
load_dotenv()
class AVM:
    def __init__(self,username, password, portal_url, portal_name, proxy,session,account_id, portal_key):
        self.username = username
        self.password = password
        self.portal_url = portal_url
        self.portal_name = portal_name
        self.proxy = proxy
        self.session = session
        self.driver = None  # Initialize driver to None
        self.portal_key = portal_key

        logging.basicConfig(level=logging.INFO)
        self.login_url = 'https://avm.assetval.com/avm/login.aspx'
        self.assignments_url = 'https://avm.assetval.com/avm/Realtor/PendingAssignments.aspx'

    

    def login_to_portal(self):
        try:
            setup_driver(self)
            self.driver.get(self.login_url)
            logging.info("Navigated to login page")

            wait = WebDriverWait(self.driver, 14)
            wait.until(EC.visibility_of_element_located((By.NAME, 'ctl00$Body$rpLogin$txtUsername'))).send_keys(self.username)
            wait.until(EC.visibility_of_element_located((By.NAME, 'ctl00$Body$rpLogin$txtPassword'))).send_keys(self.password)
            wait.until(EC.element_to_be_clickable((By.ID, 'ctl00_Body_rpLogin_btnLogin'))).click()

            # Go to Pending Assignments page
            self.driver.get(self.assignments_url)
            logging.info("Navigated to Pending Assignments page")

            self.check_alert()
            self.click_if_dashboard_button_exists()

            if self.is_logged_in():
                logging.info("Login successful")
                title = self.driver.current_url
                login_check_keyword=["PendingAssignments.aspx"]

                handle_login_status(title, username, login_check_keyword,portal_name)
                
                return "Login success", self.driver
            else:
                logging.warning("Login failed")
                self.login_status = "Login error"
                handle_login_status(self.login_status, self.username, ["False"], portal_name)
                return "Login error", self.driver

        except Exception as e:
            self.login_status = "Login error"
            logging.error("An error occurred during login: %s", str(e))
            logging.error("Error on line %s: %s", sys.exc_info()[-1].tb_lineno, type(e).__name__)
            handle_login_status(self.login_status, self.username, ["False"], portal_name)
            #update_client_account_status(self.order_id)
            return "Login error", self.driver

    # def is_logged_in(self):
    #     try:
    #         return self.driver.find_element(By.LINK_TEXT, "Log Out").is_displayed()
    #     except NoSuchElementException:
    #         logging.warning("Log Out link not found. User not logged in.")
    #         return False
    def is_logged_in(self):
        try:
            # Attempt to find the "Log Off" link by its text
            logoff_link = self.driver.find_element(By.LINK_TEXT, "Log Out")
            if logoff_link.is_displayed():
                logging.info("Log Off link is present. User is logged in.")
                return True
        except NoSuchElementException:
            # If the "Log Off" link is not found, return or handle it
            logging.warning("Log Off link not found. User is not logged in.")
            return False

    def handle_alert(self):
        try:
            alert_div = WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located((By.ID, "ctl00_Body_dvImdn"))
            )
            if alert_div.is_displayed():
                logging.info("Confirmation popup found.")
                checkbox = self.driver.find_element(By.ID, "ctl00_Body_chkIAgree")
                if not checkbox.is_selected():
                    checkbox.click()
                    logging.info("Checkbox selected.")
        except TimeoutException:
            logging.info("Alert not found.")
        except NoSuchElementException:
            logging.info("Required alert element not found.")
        except Exception as e:
            logging.error(f"Unexpected error during alert handling: {e}")

    def check_alert(self):
        try:
            alert = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "ctl00_Body_dvImdn")) 
            )
            self.handle_alert()
        except TimeoutException:
            logging.info("No alert found — continuing.")


    
    def click_if_dashboard_button_exists(driver):
        """Clicks the dashboard button if it exists."""
        try:
            buttons = driver.find_elements(By.XPATH, '//*[@id="btnDashboard"]')
            if buttons:
                buttons[0].click()
                logging.info("Dashboard button clicked.")
            else:
                logging.info("Dashboard button not found — continuing the flow.")
        except Exception as e:
            logging.error(f"Error while checking for dashboard button: {e}")        
            #return False
        # finally:
        #     if self.driver:
        #         self.driver.quit()
    # def close_browser(self):
    #     if self.driver:
    #         self.driver.quit()
