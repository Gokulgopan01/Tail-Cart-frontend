import re
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
from condtions.redbell import generate_condition_data
from config import env
from integrations.hybrid_bpo_api import HybridBPOApi
from utils.helper import clearing, data_filling_text, data_filling_text_QC, extract_data_sections, get_cookie_from_api, get_nested, get_order_address_from_assigned_order, handle_login_status, javascript_excecuter_filling, load_form_config_and_data, params_check, radio_btn_click, select_checkboxes_from_list, select_field, setup_driver, single_source_save_form, update_client_account_status, update_order_status
# Load environment variables from the .env file
load_dotenv()
arg1, arg2,arg3 = params_check()
class SingleSource:
    def __init__(self,username, password, portal_url, portal_name, proxy,session):
        self.username = username
        self.password = password
        self.portal_url = portal_url
        self.portal_name = portal_name
        self.proxy = proxy
        self.session = session
        self.driver = None  # Initialize driver to None
        self.order_details = None
        self.order_id = None
        logging.basicConfig(level=logging.INFO)
    def login_to_portal(self):
        try:
            setup_driver(self)
            session = None

            api_url = env.AUTHENTICATOR_API_URL
            headers = {'Content-Type': env.API_HEADERS_CONTENT_TYPE}
            payload = json.dumps({"username": self.username, "portal": "single_source"})

            response = requests.post(api_url, headers=headers, data=payload)
            #response.raise_for_status()
            api_response = response.json()

            if api_response.get("status") == "success":
                ss_cookie = api_response["cookies"].get("twoFactorRemember")

                if ss_cookie:
                    self.driver.get(self.portal_url)
                    self.driver.add_cookie({
                        'name': 'twoFactorRemember',
                        'value': ss_cookie
                    })

                    self.driver.get(f"{self.portal_url}")
                    self.driver.find_element(By.NAME, "txt_username").send_keys(self.username)
                    self.driver.find_element(By.NAME, "txt_password").send_keys(self.password)
                    self.driver.find_element(By.XPATH, "//input[@type='submit']").click()
                    time.sleep(2)

                    current_url = self.driver.current_url
                    if "SS_Vendor_Login.aspx" in current_url:
                        logging.error("Login failed: stayed on login page")
                    elif "UserUpdate.aspx" in current_url:
                        logging.info("Redirected to password update page")
                    elif "MFA.aspx" in current_url:
                        logging.warning("MFA encountered")
                    elif "main.aspx" in current_url:
                        logging.info("Login successful")

                        arg1 = "SmartEntry"  # Manually set for testing
                        #arg1="PortalLogin"
                        #arg1="AutoLogin"
                        if arg1 == "SmartEntry":
                            self.handle_post_login_frames()
                            self.singleSource_formopen(
                                session=session,
                                merged_json=None,
                                order_details=self.order_details,
                                order_id=self.order_id
                            )
                            return session
                        else:
                            login_check_keyword = ["main.aspx"]
                            handle_login_status(current_url, self.username, login_check_keyword, self.portal_name)
                            return session
                    else:
                        logging.error(f"Unexpected redirect: {current_url}")
                else:
                    logging.error("Cookie 'twoFactorRemember' not found in API response.")
            else:
                logging.error(f"API call failed: {api_response.get('status')}")

            update_order_status(self.order_id, "In Progress", "Entry", "Failed")

        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {e}")
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON response: {e}")
        except Exception as e:
            logging.exception(f"An unexpected error occurred during login: {e}")



        # Final fallback in case of failure
        title = "MFA FAILED"
        login_check_keyword = ["False"]
        update_order_status(self.order_id, "In Progress", "Entry", "Failed")
        update_client_account_status(self.order_id)
        handle_login_status(title, self.username, login_check_keyword, self.portal_name)
        return None, None

    def handle_post_login_frames(self):
        wait = WebDriverWait(self.driver, 20)

        try:
            self.driver.switch_to.frame("_MAIN")
            skip_button_xpath = '//*[@id="Form1"]/div[3]/div[3]/button[2]'
            wait.until(EC.element_to_be_clickable((By.XPATH, skip_button_xpath))).click()
            logging.info("Clicked skip/confirmation button in _MAIN frame")
            self.driver.switch_to.default_content()
            time.sleep(3)

            self.driver.switch_to.frame("_TOP_MENU")
            tab_xpath = '//*[@id="dl_screen_tabs"]/tbody/tr/td[2]/table/tbody/tr/td/a'
            wait.until(EC.element_to_be_clickable((By.XPATH, tab_xpath))).click()
            logging.info("Clicked second tab in _TOP_MENU frame")
            self.driver.switch_to.default_content()
            time.sleep(3)
            return self.driver # Return both driver and session

        except Exception as e:
            logging.error(f"Error navigating frames: {e}")
            self.driver.switch_to.default_content()
            return self.driver  # Return anyway, even if error

    def singleSource_formopen(self,session, merged_json, order_details, order_id):
        try:
            orders_from_api = HybridBPOApi.get_entry_order(arg2) 
            if not orders_from_api:  # Check if the order list is empty
                print("No orders found.")
                return
            
            # Process each order
            for order_from_api in orders_from_api:
                portal_name = order_from_api.get("portal_name", "")
                username = order_from_api.get("username", "")
                password = order_from_api.get("password", "")
                portal_url = order_from_api.get("portal_url", "")
                proxy = order_from_api.get("proxy", None)  # Optional proxy
                sessions=order_from_api.get("session",None)
                order_id=order_from_api.get("order_id","")
                order_details_from_api=get_order_address_from_assigned_order(order_id,arg3)
                print("order_details_from_api:", order_details_from_api)
                # if not order_details_from_api:
                #     messagebox.showerror("Authentication Required", "Please log in again.")
                #     self.controller.show_frame("EcesisLoginScreen")
                #     return
            logging.info("Starting form open process")
            target_genorderid =order_details_from_api

            form_type = [
                'FMC BPO Exterior Evaluation', 'Resolute As Repaired BPO', 'New BPO Exterior',
                'BPO Exterior', 'Exterior Evaluation'
            ]

            get_url = self.driver.current_url
            logging.info(f"Current URL in formopen_fill: {get_url}")

            if 'main' in get_url:
                print('Refreshing Portal')
                self.driver.switch_to.parent_frame()
                self.driver.switch_to.frame("_MAIN")
                time.sleep(5)

                table = self.driver.find_element(By.XPATH, '//*[@id="Form1"]/table/tbody/tr/td/table[3]')
                rows = table.find_elements(By.TAG_NAME, 'tr')

                orderidnotfound =False
                newform = 0

                if rows:
                    for row in rows:
                        print("Fetching the address")
                        cells = row.find_elements(By.TAG_NAME, 'td')
                        row_data = [cell.text for cell in cells]
                        logging.info(f"Data fetched from form: {row_data}")

                        if len(row_data) > 2:
                            portal_orderid = target_genorderid
                            portal_orderid_portal = row_data[1]
                            portal_formtype=row_data[2]

                            if (portal_orderid in portal_orderid_portal and portal_formtype in form_type) or(portal_orderid_portal in portal_orderid and portal_formtype in form_type) : 

                                logging.info(f"Address matched in form: {portal_formtype}")
                                orderidnotfound = True

                                clickable_element = cells[-1].find_element(By.TAG_NAME, 'a')
                                time.sleep(5)
                                clickable_element.click()
                                time.sleep(5)

                                try:
                                    element =  self.driver.find_element(By.XPATH, '//*[@id="form_viewer"]/tbody/tr/td/table[1]/tbody/tr/td/table')
                                except Exception as e:
                                    logging.info(f"Exception finding form element: {e}")
                                    element =  self.driver.find_element(By.XPATH, '//*[@id="form_viewer"]/tbody/tr/td/table[1]/tbody/tr/td/table/tbody/tr/td[1]/font')
                                
                                formtype_value = element.text.strip()
                                logging.info(f"Form type inside the form: {formtype_value}")
                                SingleSource_formopen_fill(self, formtype_value, session, merged_json, order_details, order_id)
                                break
                                # element = session.find_element(By.ID, "PS_FORM/RECENT_SALE1/Street_Address1")
                                # listing_address = element.get_attribute('value')
                                # logging.info(f"sale1 address: {listing_address}")

                            else:
                                logging.info(f"portal_orderid_portal not matched in the corresponding row: {portal_orderid_portal}")
                                if portal_orderid not in portal_orderid_portal:
                                    orderidnotfound += 1
                                else:
                                    newform += 1
                        else:
                            print("No orders in the portal")
                            logging.info("No orders in the portal")

                    if not orderidnotfound:
                        print("portal_orderid_portal not found")
                        logging.info(f"portal_orderid_portal not found {portal_orderid_portal}")
                        #statuschange(order_details, "29", "3" if order_desc == "X-Completed" else "16", "14")
                    else:
                        print("address completed")
                        logging.info("Address completed")
                        return

                    if newform > 0:
                        logging.info(f"Form type outside the form: {formtype_value}")
                        #statuschange(order_details, "28", "3" if order_desc == "X-Completed" else "16", "14")
                    else:
                        logging.info("Exception Form type outside the form")
                else:
                    print("No orders in the portal Address Not Found")
                    logging.info(f"No orders in the portal Address Not Found {order_details['subject_address']}")
                    #statuschange(order_details, "29", "3" if order_desc == "X-Completed" else "16", "14")

        except Exception as e:
            logging.exception(f"Exception in singleSource_formopen: {e}")       

def SingleSource_formopen_fill(self, formtype_value, session=None, merged_json=None, order_details=None, order_id=None):

    researchpad_data_retrival_url=env.RESEARCHPAD_DATA_URL
    if formtype_value=="Resolute As Repaired BPO":
        
            config_path = 'json/singlesourcejson/SingleSource_Resolute_As_Repaired_bpo.json'

    else:
        logging.warning(f"No matching config path for form type: {formtype_value}")
        update_order_status(order_id, "In Progress", "Entry", "Failed")
        return
    form_config, merged_json = load_form_config_and_data(
        order_id=order_id,
        config_path=config_path,
        researchpad_data_retrival_url=researchpad_data_retrival_url,
        session=session,
        merged_json=merged_json
    )
    # Optional: Check if loading was successful
    if not form_config or not merged_json:
        return
    # Extract and generate condition_data, attach it inside merged_json for usage if needed
    sub_data, comp_data, adj_data, rental_data,sold1,sold2,sold3, list1, list2, list3,rental_list1,rental_list2,rental_leased1,rental_leased2,adj_sold1,adj_sold2,adj_sold3,adj_list1,adj_list2,adj_list3 = extract_data_sections(merged_json)
    condition_data = generate_condition_data(sub_data, comp_data, adj_data, rental_data,sold1,sold2,sold3, list1, list2, list3,rental_list1,rental_list2,rental_leased1,rental_leased2,adj_sold1,adj_sold2,adj_sold3,adj_list1,adj_list2,adj_list3)
    if "entry_data" in merged_json and merged_json["entry_data"]:
        merged_json["entry_data"][0]["condition_data"] = condition_data

    print(merged_json)    

    try:
        # Call fill_form_multi for just this page
        form_fill=fill_form_multi(self, merged_json, order_id, form_config, session)
        time.sleep(2)

    except Exception as e:
        logging.exception(f"Error while navigating and filling forms: {e}")
        #update_order_status(order_id, "In Progress", "Entry", "Failed")
        return

def fill_form_multi(self, merged_json, order_id, form_config, session): 
        key_expr_cache = {}
        value_cache = {}

        def get_keys_cached(key_expr):
            if key_expr not in key_expr_cache:
                key_expr_cache[key_expr] = re.findall(r"\['(.*?)'\]", key_expr)
            return key_expr_cache[key_expr]

        def extract_value_from_expr(expr):
            if expr in value_cache:
                return value_cache[expr]

            data_sources = {
                "sub_data": sub_data,
                "comp_data": comp_data,
                "adj_data": adj_data,
                "rental_data": rental_data,
                "condition_data": condition_data,
                "entry_data[0]": merged_json.get("entry_data", [{}])[0],
                "sold1": sold1,
                "sold2": sold2,
                "sold3": sold3,
                "list1": list1,
                "list2": list2,
                "list3": list3,
                "rental_list1":rental_list1,
                "rental_list2":rental_list2,
                "rental_leased1":rental_leased1,
                "rental_leased2":rental_leased2,
                "adj_sold1":adj_sold1,
                "adj_sold2":adj_sold2,
                "adj_sold3":adj_sold3,
                "adj_list1":adj_list1,
                "adj_list2":adj_list2,
                "adj_list3":adj_list3
            }

            for prefix, data_source in data_sources.items():
                if expr.startswith(prefix):
                    suffix = expr[len(prefix):]
                    keys = get_keys_cached(suffix) if prefix == "entry_data[0]" else get_keys_cached(expr)
                    value = get_nested(data_source, keys, "")
                    value_cache[expr] = value
                    return value

            value_cache[expr] = expr
            return expr

        field_actions = {
            "Textbox": data_filling_text,
            "Textbox_default": data_filling_text,
            "Textbox_QC": data_filling_text_QC,
            "Textbox_default_QC": data_filling_text_QC,
            "select_data": select_field,
            "select_default": select_field,
            "radiobutton_data": radio_btn_click,
            "radiobutton_default": radio_btn_click,
            "date_fill_javascript": javascript_excecuter_filling,
            "clearing": clearing,
            "checkbox": select_checkboxes_from_list,
        }

        try:
            sub_data, comp_data, adj_data, rental_data, sold1, sold2, sold3, list1, list2, list3 ,rental_list1,rental_list2,rental_leased1,rental_leased2,adj_sold1,adj_sold2,adj_sold3,adj_list1,adj_list2,adj_list3= extract_data_sections(merged_json)
            if sub_data is None:
                logging.error("'entry_data' missing or empty in merged_json")
                update_order_status(order_id, "In Progress", "Entry", "Failed")
                return False

            condition_data = generate_condition_data(sub_data, comp_data, adj_data, rental_data, sold1, sold2, sold3, list1, list2, list3,rental_list1,rental_list2,rental_leased1,rental_leased2,adj_sold1,adj_sold2,adj_sold3,adj_list1,adj_list2,adj_list3)
            saved_form = False

            for page in form_config.get("page", []):
                controls = page.get("Controls", [])
                if not isinstance(controls, (list, tuple)):
                    logging.warning(f"Expected 'Controls' to be list but got {type(controls)}")
                    continue

                for control in controls:
                    if not isinstance(control, dict):
                        logging.warning(f"Control is not dict: {control}")
                        continue

                    field_type = control.get("filedtype")
                    values = control.get("values", [])

                    if field_type == "save_data":
                        if not saved_form:
                            single_source_save_form(self.driver)
                            logging.info("Form saved.")
                            # for cookie in self.driver.get_cookies():
                            #     session.cookies.set(cookie['name'], cookie['value'])
                            # time.sleep(5)
                            saved_form = True
                        continue
                    for field in values:
                        if not (isinstance(field, list) and len(field) == 3):
                            logging.warning(f"Invalid field format: {field}")
                            continue

                        key_expr, xpath, mode = field
                        try:
                            value = extract_value_from_expr(key_expr)

                            if value in [None, ""]:
                                continue

                            action_func = field_actions.get(field_type)
                            if action_func:
                                action_func(self.driver, value, xpath, mode)
                            else:
                                logging.warning(f"Unknown field type: {field_type}")
                        except Exception as e:
                            logging.error(f"Exception filling field {key_expr}: {e}")

            if saved_form:
                #update_order_status(order_id, "In Progress", "Entry", "Completed")
                return True
            else:
                #update_order_status(order_id, "In Progress", "Entry", "Failed")
                return False

        except Exception as e:
            logging.error(f"Critical error in fill_form_multi: {e}")
            #update_order_status(order_id, "In Progress", "Entry", "Failed")
            return False



            