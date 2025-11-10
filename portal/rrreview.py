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
from dotenv import load_dotenv
import os
from selenium.webdriver.support.ui import WebDriverWait, Select
from config import env
load_dotenv()
from condtions.all_portal_conditions import generate_condition_data
from utils.helper import extract_data_sections, get_cookie_from_api, get_order_address_from_assigned_order, handle_login_status, load_form_config_and_data, params_check, setup_driver, update_client_account_status, update_order_status
from integrations.hybrid_bpo_api import HybridBPOApi
arg1, arg2,arg3 = params_check()
print(arg1,arg2,arg3)
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
                return
            

            for order_from_api in orders_from_api:
                portal_name = order_from_api.get("portal_name", "")
                username = order_from_api.get("username", "")
                password = order_from_api.get("password", "")
                portal_url = order_from_api.get("portal_url", "")
                proxy = order_from_api.get("proxy", None)  # Optional proxy
                session=order_from_api.get("session",None)
                hyorder_id=order_from_api.get("order_id","")
                portal_order_id=order_from_api.get("portal_orderid","")
                order_details_from_api,tfs_orderid=get_order_address_from_assigned_order(hyorder_id,arg3)
                print("order_details_from_api:", order_details_from_api)
                print("tfs",tfs_orderid)
                print("ID:",portal_order_id)
            
            # --- Step 2: Parse ALL Active Orders in RRR portal ---
            
            print("Fetching all portal order IDs and Form Types from RRR...")

            # Wait for all order rows to load completely
            order_rows = WebDriverWait(self.driver, 30).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//ion-row[contains(@class, 'data-row')]")
                )
            )

            # Dictionary to store order_id -> form_type
            portal_order_data = {}

            for row in order_rows:
                try:
                    # Column 1: Order ID
                    order_id_el = row.find_element(By.XPATH, ".//ion-col[1]//ion-label")
                    portalorder_id = order_id_el.text.strip()

                    # Column 2: Form Type
                    form_type_el = row.find_element(By.XPATH, ".//ion-col[2]//ion-label")
                    form_type = form_type_el.text.strip()

                    # Only store valid numeric order IDs
                    if portalorder_id.isdigit():
                        portal_order_data[portalorder_id] = form_type
                except Exception as e:
                    logging.warning(f"Skipping a row due to parsing error: {e}")
                    continue

            print(f"Parsed Portal Order Data: {portal_order_data}")

            # Extract HybridBPO order IDs for matching
            hybrid_order_id = [str(o.get("portal_orderid", "")).strip() for o in orders_from_api if o.get("portal_orderid")]

            # Find common order IDs
            matched_order = [oid for oid in portal_order_data.keys() if oid in hybrid_order_id]
            print(f"Matched Order: {matched_order}")

            # Optional: define allowed form types for SmartEntry
            allowed_form_types = ["EXTERIOR BPO"]

            # Click only matched orders **with allowed form type**
            for order_id in matched_order:
                form_type = portal_order_data.get(order_id)
                if form_type in allowed_form_types:
                    print(f"Opening order {order_id} with form type {form_type}")
                    self.click_order_by_id(order_id)
                    
                    # Proceed to form fill once open
                    self.rrreview_formopen_fill(form_type,hyorder_id,self.session,merged_json=None)

                else:
                    print(f"Skipping order {order_id} with unsupported form type: {form_type}")

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
      
    def rrreview_formopen_fill(self,formtype_value,order_id,session,merged_json):
        """Handles mapping config, merged_json loading, and form-filling for RRReview SmartEntry."""
        try:
            # Load ResearchPad API endpoint from environment
            researchpad_data_retrival_url=env.RESEARCHPAD_DATA_URL
            print(researchpad_data_retrival_url)

            #  Step 1: Choose JSON config path based on form type
            if formtype_value == "EXTERIOR BPO":
                print("yes")
                config_path = 'json/rrreviewjson/RRReview_Exterior_BPO.json'
            else:
                logging.warning(f"No matching config path found for form type: {formtype_value}")
                update_order_status(order_id, "In Progress", "Entry", "Failed")
                return
            
            form_config, merged_json = load_form_config_and_data(
            order_id=order_id,
            config_path=config_path,
            researchpad_data_retrival_url=researchpad_data_retrival_url,
            session=self.session,
            merged_json=merged_json
            )
            if not form_config or not merged_json:
              logging.warning(f"Config or data missing for order {order_id}")
              return 
        
            # Extract and generate condition_data, attach it inside merged_json for usage if needed
            sub_data, comp_data, adj_data, rental_data,sold1,sold2,sold3, list1, list2, list3,rental_list1,rental_list2,rental_leased1,rental_leased2,adj_sold1,adj_sold2,adj_sold3,adj_list1,adj_list2,adj_list3 = extract_data_sections(merged_json)
            condition_data = generate_condition_data(sub_data, comp_data, adj_data, rental_data,sold1,sold2,sold3, list1, list2, list3,rental_list1,rental_list2,rental_leased1,rental_leased2,adj_sold1,adj_sold2,adj_sold3,adj_list1,adj_list2,adj_list3)
            if "entry_data" in merged_json and merged_json["entry_data"]:
                merged_json["entry_data"][0]["condition_data"] = condition_data

          
            # print("MERGED JSON:",merged_json)

            try:
                # Call fill_form_multi for just this page
                self.fill_form_multi(merged_json, order_id, form_config, session)
                time.sleep(2)

            except Exception as e:
                logging.exception(f"Error while navigating and filling forms: {e}")
                return
        except Exception as e:
            logging.exception(f"Exception in rrreview_formopen_fill: {e}")
            pass

    # def fill_form_multi(self, merged_json, order_id, form_config, session):
    #     print("Filling form now...")
    



    # def fill_form_multi(self, merged_json, order_id, form_config, session):
    #     """
    #     SmartEntry: Auto-fills form fields across multiple tabs dynamically
    #     using the configuration defined in form_config.json
    #     and data from merged_json.
    #     """
    #     driver = self.driver
    #     print("🚀 Starting SmartEntry multi-tab form filling...")
    #     print(f"Order ID: {order_id}")

    #     try:
    #         # ✅ Extract subject data from merged_json
    #         sub_data = merged_json.get("entry_data", [{}])[0].get("sub_data", {})
    #         form_pages = form_config.get("page", [])
    #         print("📄 Loaded form configuration:", form_pages)

    #         # ✅ Loop through each page/tab in the form config
    #         for page in form_pages:
    #             for tab_name, fields in page.items():
    #                 print(f"\n🔹 Switching to tab: {tab_name}")
    #                 tab_xpath = f"//a[contains(@class, 'ui-tabs-anchor') and normalize-space(text())='{tab_name}']"

    #                 # Switch to tab
    #                 try:
    #                     WebDriverWait(driver, 10).until(
    #                         EC.element_to_be_clickable((By.XPATH, tab_xpath))
    #                     ).click()
    #                     time.sleep(1)
    #                 except Exception:
    #                     print(f"⚠️ Unable to switch to tab {tab_name}")
    #                     continue

    #                 # ✅ Fill each field defined for this tab
    #                 for field in fields:
    #                     fieldtype = field.get("filedtype", "").lower()
    #                     values = field.get("values", [])
    #                     for val in values:
    #                         try:
    #                             data_expr, xpath, locator_type = val
    #                             print(f"➡️ Processing field: {data_expr} | {xpath}")

    #                             # ✅ Evaluate data expression safely
    #                             value = None
    #                             if "sub_data" in data_expr:
    #                                 try:
    #                                     value = eval(data_expr, {"sub_data": sub_data})
    #                                 except Exception as e:
    #                                     print(f"⚠️ Failed to eval sub_data expr {data_expr}: {e}")
    #                             else:
    #                                 try:
    #                                     value = eval(data_expr, {"merged_json": merged_json})
    #                                 except Exception:
    #                                     value = merged_json.get(data_expr.strip("'"), None)

    #                             # Skip if value is empty
    #                             if not value or str(value).strip() == "":
    #                                 print(f"⏭️ Skipping empty value for {data_expr}")
    #                                 continue

    #                             # ✅ Locate field element
    #                             element = WebDriverWait(driver, 10).until(
    #                                 EC.presence_of_element_located((By.XPATH, xpath))
    #                             )
    #                             driver.execute_script("arguments[0].scrollIntoView(true);", element)
    #                             time.sleep(0.3)

    #                             # ✅ Fill based on field type
    #                             if fieldtype == "textbox":
    #                                 element.clear()
    #                                 element.send_keys(str(value))
    #                                 print(f"🟢 Textbox filled: {xpath} = {value}")

    #                             elif fieldtype == "select_data":
    #                                 try:
    #                                     Select(element).select_by_visible_text(str(value))
    #                                     print(f"🟢 Dropdown selected: {xpath} = {value}")
    #                                 except Exception:
    #                                     element.send_keys(str(value))
    #                                     print(f"🟢 Dropdown fallback send_keys: {xpath} = {value}")

    #                             elif fieldtype == "checkbox":
    #                                 if str(value).lower() in ["yes", "true", "1"]:
    #                                     if not element.is_selected():
    #                                         element.click()
    #                                         print(f"🟢 Checkbox checked: {xpath}")

    #                         except Exception as e:
    #                             print(f"⚠️ Error filling field {val}: {e}")
    #                             continue

    #         print("\n✅ All fields processed successfully for order:", order_id)

    #     except Exception as e:
    #         logging.exception(f"❌ Error while filling SmartEntry form: {e}")
    
    def fill_form_multi(self, merged_json, order_id, form_config, session):
        """
        Smart Entry auto-filling for RRReview form.
        Handles multiple tabs and iframes using form_config mapping.
        """
        driver = self.driver
        print("🚀 Starting SmartEntry form auto-fill for order:", order_id)

        try:
            # Extract the sub_data block (subject property data)
            sub_data = merged_json.get("entry_data", [{}])[0].get("sub_data", {})
            formdata = form_config.get("page", [])

            # Loop through each page (tab)
            for page in formdata:
                for tab_name, fields in page.items():
                    print(f"\n🔹 Switching to tab: {tab_name}")

                    # Construct tab and iframe IDs dynamically
                    tab_xpath = f"//a[contains(@class, 'ui-tabs-anchor') and normalize-space(text())='{tab_name}']"

                    # --- STEP 1: Click the tab ---
                    WebDriverWait(driver, 15).until(
                        EC.element_to_be_clickable((By.XPATH, tab_xpath))
                    ).click()
                    time.sleep(1)

                    # --- STEP 2: Switch to corresponding iframe ---
                    iframe_id_map = {
                        "Work Order Detail": "iframeBPOBPOEntryFormTab1",
                        "Subject Information": "iframeBPOBPOEntryFormTab2",
                        "Repair Information": "iframeBPOBPOEntryFormTab3",
                        "Comparable Information": "iframeBPOBPOEntryFormTab4",
                        "Photos/Documents": "iframeBPOBPOEntryFormTab5",
                        "Validation Results": "iframeBPOBPOEntryFormTab6",
                    }
                    iframe_id = iframe_id_map.get(tab_name)

                    driver.switch_to.default_content()
                    if iframe_id:
                        try:
                            iframe = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.ID, iframe_id))
                            )
                            driver.switch_to.frame(iframe)
                            print(f"Switched to iframe: {iframe_id}")
                        except Exception:
                            print(f"Could not locate iframe {iframe_id}, continuing in main content.")
                    else:
                        print(f"No iframe mapping found for tab '{tab_name}'")

                    # --- STEP 3: Fill fields from config ---
                    for field in fields:
                        fieldtype = field.get("filedtype", "").lower()
                        values = field.get("values", [])

                        for val in values:
                            try:
                                data_expr, xpath, locator_type = val
                                print(f"Filling {data_expr} → {xpath}")

                                # Safely evaluate expression from JSON (e.g., sub_data['City'])
                                try:
                                    value = eval(data_expr, {"merged_json": merged_json, "sub_data": sub_data})
                                except Exception:
                                    value = merged_json.get(data_expr.strip("'"), None)

                                if not value or str(value).strip() == "":
                                    continue

                                # Wait for the element
                                element = WebDriverWait(driver, 15).until(
                                    EC.presence_of_element_located((By.XPATH, xpath))
                                )

                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                                time.sleep(0.4)

                                # --- Fill element based on fieldtype ---
                                if fieldtype == "textbox":
                                    element.clear()
                                    element.send_keys(str(value))
                                    print(f"Textbox filled: {xpath} = {value}")

                                elif fieldtype == "select_data":
                                    try:
                                        Select(element).select_by_visible_text(str(value))
                                        print(f"Dropdown selected: {xpath} = {value}")
                                    except Exception:
                                        element.send_keys(str(value))
                                        print(f"Dropdown fallback send_keys: {xpath} = {value}")

                                elif fieldtype == "checkbox":
                                    if str(value).lower() in ["yes", "true", "1"]:
                                        if not element.is_selected():
                                            element.click()
                                            print(f"Checkbox checked: {xpath}")

                            except Exception as e:
                                print(f" Error filling field {val}: {e}")
                                continue

                    # --- STEP 4: Exit current iframe before moving to next tab ---
                    driver.switch_to.default_content()
                    print(f"Returned to main page after '{tab_name}' tab.\n")

            print("\nSmart Entry filling completed for all tabs.")

        except Exception as e:
            logging.exception(f"Error while filling SmartEntry form: {e}")
            driver.switch_to.default_content()

