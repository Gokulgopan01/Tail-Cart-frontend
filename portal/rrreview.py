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

from utils.helper import get_cookie_from_api, get_order_address_from_assigned_order, handle_login_status, params_check, setup_driver, update_client_account_status
from integrations.hybrid_bpo_api import HybridBPOApi
arg1, arg2,arg3 = params_check()
# Load environment variables from the .env file
load_dotenv()
class rrreview:
    def __init__(self, username, password, portal_url, portal_name, proxy, session):
        self.username = username
        self.password = password
        self.portal_url = portal_url
        self.portal_name = portal_name
        self.proxy = proxy
        self.driver = None
        self.session=session
        self.login_status = "Not started"
        logging.basicConfig(level=logging.INFO)


    def login_to_portal(self):
        try:
    
            # Step 1: Setup WebDriver
            setup_driver(self)

            api_response = get_cookie_from_api(self.username, portal="rrr", proxy=self.proxy)
            print(api_response)
            if not api_response:
                self.login_status = "API response error"
                handle_login_status("API_FAILED", self.username, ["VendorPortal/Index"], self.portal_name)
                return "Login error", self.driver
            # Step 3: Inject session storage
            self.driver.get('https://www.rrreview.com/runtime.aa40cd539422f2485b46.js')
            time.sleep(1)

            for key, value in api_response.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        self.driver.execute_script(f"sessionStorage.setItem('{sub_key}', '{sub_value}');")
                else:
                    self.driver.execute_script(f"sessionStorage.setItem('{key}', '{value}');")

            # Step 4: Navigate to Active Orders
            self.driver.get('https://www.rrreview.com/#/baseauth/activeorders')
            time.sleep(5)

            # Step 5: Check if Login Successful
            current_url = self.driver.current_url
            print(current_url)
            # if 'https://www.rrreview.com/#/baseauth/activeorders' in current_url:
            #     logging.info("Login successful")
            #     return "Login success", self.driver
            # else:
            #     logging.error(f"Login failed. URL landed: {current_url}")
            #     return "Login error", self.driver
            # handle_login_status(current_url, self.username, ["baseauth/activeorders"], self.portal_name)
                
                # handle_login_status(current_url, self.username, success_keywords, self.portal_name)
                # return self.login_status, self.driver

            arg1 = "SmartEntry"  # Manually set for testing
            #arg1="PortalLogin"
            #arg1="AutoLogin"
            if arg1 == "SmartEntry":
                self.rrreview_formopen()
            else:
                login_check_keyword = ["baseauth/activeorders"]
                handle_login_status(current_url, self.username, login_check_keyword, self.portal_name)

          
        except Exception as e:
            self.login_status = f"Exception occurred: {e}"
            logging.exception("Exception during login")
            handle_login_status("EXCEPTION", self.username, ["activeorders"], self.portal_name)
            #update_client_account_status(self.order_id)
            return "Login error", self.driver
        
    def rrreview_formopen(self):
        try:
            orders_from_api = HybridBPOApi.get_entry_order(arg2)
            if not orders_from_api:  # Check if the order list is empty
                print("No orders found.")

            for order_from_api in orders_from_api:
                portal_name = order_from_api.get("portal_name", "")
                username = order_from_api.get("username", "")
                password = order_from_api.get("password", "")
                portal_url = order_from_api.get("portal_url", "")
                proxy = order_from_api.get("proxy", None)  # Optional proxy
                sessions=order_from_api.get("session",None)
                order_id=order_from_api.get("order_id","")
                portal_order_id=order_from_api.get("portal_orderid","")
                order_details_from_api,tfs_orderid=get_order_address_from_assigned_order(order_id,arg3)
                print("order_details_from_api:", order_details_from_api)
                print("tfs",tfs_orderid)
                print("ID:",portal_order_id)
            
            # #parsing active orders order id's   
            # element_xpath = "//ion-row[contains(@class, 'data-row')]/ion-col[1]//ion-label"
            # response = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.XPATH, element_xpath)))
            # portal_order_id = response.text.strip()
            # print(f"Portal Order ID: {portal_order_id}")
            

                # --- Step 2: Parse ALL Active Orders in RRR portal ---
            print("Fetching all portal order IDs from RRR...")

             # Wait for all portal orders to load
            order_elements = WebDriverWait(self.driver, 30).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//ion-row[contains(@class, 'data-row')]/ion-col[1]//ion-label")
                )
            )

            # Extract only valid numeric order IDs
            portal_order_ids = [el.text.strip() for el in order_elements if el.text.strip().isdigit()]
            print(f"Total {len(portal_order_ids)} orders found on portal: {portal_order_ids}")

            # Extract Hybrid BPO order ID for comparison
            hybrid_order_id = [str(o.get("portal_orderid", "")).strip() for o in orders_from_api if o.get("portal_orderid")]

           
            matched_order = [oid for oid in portal_order_ids if oid in hybrid_order_id]
            print(f"Matched Order: {matched_order}")

            # Click matched orders one by one
            for order_id in matched_order:
                self.click_order_by_id(order_id)
               

        except Exception as e:
            logging.exception(f"Exception in rrreview_formopen: {e}")

    def click_order_by_id(self, order_id):
        """Find and click the given order ID on the RRR portal dashboard."""
        try:
            print(f"Looking for order {order_id}...")

            # Wait for all order labels to load completely
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//ion-label[contains(@class, 'textunderline')]")
                )
            )

            # Get all ion-label elements with order IDs
            labels = self.driver.find_elements(
                By.XPATH, "//ion-label[contains(@class, 'textunderline')]"
            )

            target = None
            for label in labels:
                text = label.text.strip()
                if order_id in text:
                    target = label
                    break

            if not target:
                raise Exception(f"Order {order_id} not found among portal orders.")

            # Scroll into view
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", target)
            time.sleep(1)

            # Use JavaScript click (Ionic click is often JS-handled)
            self.driver.execute_script("arguments[0].click();", target)
            print(f"Successfully clicked order {order_id}")

            # Optional: wait a bit for navigation or popup
            time.sleep(3)


            try:
                    print("Looking for 'I am ready to enter data or submit report' button...")

                    # Wait until the button is visible & clickable
                    ready_button = WebDriverWait(self.driver, 20).until(
                        EC.element_to_be_clickable((
                            By.XPATH, "//ion-button[.//span[normalize-space()='I am ready to enter data or submit report']]"
                        ))
                    )

                    # Use native Selenium click 
                    self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", ready_button)
                    time.sleep(1)  # small pause so Angular attaches handlers
                    ready_button.click()  

                    print("Button clicked, waiting for form to open...")

                    # Now wait for the form submitorder button
                    WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located((By.XPATH, "//*[@id='submitorderbutton']"))
                    )
                    print("Form loaded successfully!")

            except Exception as e:
                    print(f"Could not open the form: {e}")

        except Exception as e:
            logging.exception(f"Could not click order {order_id}: {e}")
