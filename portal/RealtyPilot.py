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
class RealtyPilot:
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
            setup_driver(self)
            self.driver.get(self.portal_url)
            logging.info(f"Navigated to {self.portal_url}")

            # Wait for and enter Username
            WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.NAME, "login"))
            ).clear()
            self.driver.find_element(By.NAME, "login").send_keys(self.username)

            # Wait for and enter Password
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.NAME, "password"))
            ).send_keys(self.password)

            # Click Login button
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "sign_in"))
            ).click()

            current_title = self.driver.title
            logging.info(f"Page title after login: {current_title}")

            login_check_keywords = ["Administrator Panel"]
            handle_login_status(current_title, self.username, login_check_keywords, self.portal_name)

            return self.driver

        except Exception as e:
            self.login_status = f"Exception occurred: {e}"
            logging.exception("Exception during login")
            handle_login_status("EXCEPTION", self.username, ["Exception during login"], self.portal_name)
            #update_client_account_status(self.order_id)
            return "Login error", self.driver

 