import re
import time
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import logging
from dotenv import load_dotenv
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

                   

import logging
import requests
import json
import os
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
import os
from selenium.webdriver.support.ui import WebDriverWait, Select
from config import env
load_dotenv()
from condtions.all_portal_conditions import generate_condition_data
from utils.helper import data_filling_text, extract_data_sections, get_cookie_from_api, get_nested, get_order_address_from_assigned_order, handle_login_status, javascript_excecuter_filling, load_form_config_and_data, params_check, radio_btn_click, rrr_fill_repair_details, save_form, save_form_adj, select_checkboxes_from_list, select_field, setup_driver, tfs_statuschange, update_client_account_status, update_order_status
from integrations.hybrid_bpo_api import HybridBPOApi
# arg1, arg2,arg3 = params_check()
# print(arg1,arg2,arg3)

process_type, hybrid_orderid,hybrid_token = params_check()
logging.info(f"type,orderid,token,{process_type},{hybrid_orderid},{hybrid_token}")
# Load environment variables from the .env file
load_dotenv()
class rrreview:
    def __init__(self, username, password, portal_url, portal_name, proxy, session,account_id):
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

        except Exception as e:
            self.login_status = f"Exception occurred: {e}"
            logging.exception("Exception during login")
            handle_login_status("EXCEPTION", self.username, ["activeorders"], self.portal_name)
            #update_client_account_status(self.order_id)
            return "Login error", self.driver
