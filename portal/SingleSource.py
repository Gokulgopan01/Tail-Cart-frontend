import re
import time
import tkinter as tk
from tkinter import ttk, messagebox
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
from condtions.all_portal_conditions import generate_condition_data
from config import env
from integrations.hybrid_bpo_api import HybridBPOApi
from utils.helper import SS_fill_repair_details, adj_click, close_validation_popup, data_filling_text, extract_data_sections, fetch_upload_data, get_cookie_from_api, get_nested, get_order_address_from_assigned_order, handle_login_status, javascript_excecuter_filling, load_form_config_and_data, params_check, radio_btn_click, select_checkboxes_from_list, select_field, setup_driver, single_source_save_form, update_client_account_status, update_order_status, update_portal_login_confirmation_status
# Load environment variables from the .env file
load_dotenv()
process_type, hybrid_orderid,hybrid_token = params_check()
class SingleSource:
    def __init__(self,username, password, portal_url, portal_name, proxy,session,account_id):
        self.username = username
        self.password = password
        self.portal_url = portal_url
        self.portal_name = portal_name
        self.proxy = proxy
        self.session = session
        self.driver = None  # Initialize driver to None
        self.order_details = None
        self.order_id = None
        self.account_id=account_id
        logging.basicConfig(level=logging.INFO)
    def login_to_portal(self):
        try:
            setup_driver(self)
            session = None

            api_url = env.AUTHENTICATOR_API_URL
            headers = {'Content-Type': env.API_HEADERS_CONTENT_TYPE}
            payload = json.dumps({"username": self.username, "portal": "single_source"})

            response = requests.post(api_url, headers=headers, data=payload ,timeout=190)
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

                        #process_type = "SmartEntry"  # Manually set for testing
                        #process_type="PortalLogin"
                        #process_type="AutoLogin"
                        if process_type == "SmartEntry":
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
                            update_portal_login_confirmation_status(hybrid_orderid)
                            handle_login_status(current_url, self.username, login_check_keyword, self.portal_name)
                            #update_portal_login_confirmation_status(hybrid_orderid)
                            return session
                    else:
                        logging.error(f"Unexpected redirect: {current_url}")
                else:
                    logging.error("Cookie 'twoFactorRemember' not found in API response.")
            else:
                logging.error(f"API call failed: {api_response.get('status')}")

            update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)

        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {e}")
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON response: {e}")
        except Exception as e:
            logging.exception(f"An unexpected error occurred during login: {e}")



        # Final fallback in case of failure
        title = "MFA FAILED"
        login_check_keyword = ["False"]
        update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
        update_client_account_status(self.account_id)
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
            orders_from_api = HybridBPOApi.get_entry_order(hybrid_orderid) 
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
                order_details_from_api,tfs_orderid=get_order_address_from_assigned_order(order_id,hybrid_token)
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
    # Normalize form type
    norm_formtype = formtype_value.strip()

    if norm_formtype in ["Resolute As Repaired BPO" ,"Resolute As Repaired BPO Needs Corrections."]:
        config_path = 'json/singlesourcejson/SingleSource_Resolute_As_Repaired_bpo.json'
    elif norm_formtype in["SS New BPO Exterior-SHP" ,"SS New BPO Exterior-SHP Needs Corrections."]:
        config_path = 'json/singlesourcejson/SingleSource_SS_New_BPO_Exterior_SHP.json'
    elif norm_formtype in ["SS New BPO Exterior", "BPO Exterior","SS New BPO Exterior Needs Corrections."]:
        config_path = 'json/singlesourcejson/SingleSource_SS_New_BPO_Exterior.json'        
    else:
        logging.warning(f"No matching config path for form type: {formtype_value}")
        update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
        return
    form_config, merged_json = load_form_config_and_data(
        order_id=order_id,
        config_path=config_path,
        researchpad_data_retrival_url=researchpad_data_retrival_url,
        session=session,
        merged_json=merged_json,token=hybrid_token
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
    
    try:

        data = fetch_upload_data(self, order_id)
        if not data:
            logging.warning(f"No upload data found for order {order_id}")
            update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
            return
        mls_result = upload_mls_for_order(self,order_id)
        tax_result = upload_tax_for_order(self,order_id)
        comparables_folder = data.get("comparables_folder")
        # rental_folder = data.get("rental_folder")
        # photos_url = page_urls["Photos"]

        if isinstance(comparables_folder, str) and comparables_folder.strip():
            upload_photos=upload_photos_to_order(self, comparables_folder)
        else:
            logging.warning(f"Comparables folder is missing or invalid for order {order_id}: {comparables_folder!r}")
            update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
        # Check if all 3 are True
        if form_fill and mls_result and tax_result and upload_photos:
            logging.info("All form filling and upload functions completed successfully.")
            update_order_status(hybrid_orderid, "In Progress", "Entry", "Completed",hybrid_token)
        else:
            logging.warning(f"One or more functions failed: form_fill={form_fill}, upload_photos={upload_photos}")
            update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
    except Exception as e:
        logging.exception(f"Error during photo upload steps: {e}")
        update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
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
            "select_data": select_field,
            "select_default": select_field,
            "radiobutton_data": radio_btn_click,
            "radiobutton_default": radio_btn_click,
            "date_fill_javascript": javascript_excecuter_filling,
            "checkbox": select_checkboxes_from_list,
        }

        try:
            sub_data, comp_data, adj_data, rental_data, sold1, sold2, sold3, list1, list2, list3 ,rental_list1,rental_list2,rental_leased1,rental_leased2,adj_sold1,adj_sold2,adj_sold3,adj_list1,adj_list2,adj_list3= extract_data_sections(merged_json)
            if sub_data is None:
                logging.error("'entry_data' missing or empty in merged_json")
                update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
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

                    if field_type == "validation_popup":
                        close_validation_popup(self.driver)

                    if field_type == "save_data":
                        if not saved_form:
                            single_source_save_form(self.driver)
                            logging.info("Form saved.")
                            # for cookie in self.driver.get_cookies():
                            #     session.cookies.set(cookie['name'], cookie['value'])
                            # time.sleep(5)
                            saved_form = True
                        continue
                    # if field_type == "repair_details_fill":
                    #     for field in values:
                    #         # Validate field format
                    #         if not (isinstance(field, list) and len(field) >= 3):
                    #             logging.warning(f"Invalid repair_details_fill field: {field}")
                    #             continue

                    #         key_expr, _, _ = field
                    #         try:
                    #             # Extract the list of repairs from your JSON
                    #             repairs_list = extract_value_from_expr(key_expr)
                    #             if isinstance(repairs_list, list):
                    #                 # Fill only estimated_costs, ignoring comments
                    #                 SS_fill_repair_details(self.driver, repairs_list)
                    #                 logging.info(f"Filled repair details for {key_expr}")
                    #             else:
                    #                 logging.warning(f"Expected list for repair details but got: {repairs_list}")
                    #         except Exception as e:
                    #             logging.error(f"Error processing repair_details_fill for {key_expr}: {e}")
                    #     continue

                    if field_type == "repair_details_fill":
                        for field in values:
                            # Validate field format
                            if not (isinstance(field, list) and len(field) >= 3):
                                logging.warning(f"Invalid repair_details_fill field: {field}")
                                continue

                            key_expr, _, _ = field
                            try:
                                # Extract the full repair_details dict from JSON
                                repair_details = extract_value_from_expr(key_expr)
                                
                                if isinstance(repair_details, dict) and "repairs" in repair_details:
                                    SS_fill_repair_details(self.driver, repair_details)
                                    logging.info(f"Filled repair details for {key_expr}")
                                else:
                                    logging.warning(f"Expected dict with 'repairs' for repair details but got: {repair_details}")
                            except Exception as e:
                                logging.error(f"Error processing repair_details_fill for {key_expr}: {e}")
                        continue


                    for field in values:
                        if not (isinstance(field, list) and len(field) == 3):
                            logging.warning(f"Invalid field format: {field}")
                            continue

                        key_expr, xpath, mode = field
                        value = extract_value_from_expr(key_expr)

                        if value in [None, ""]:
                            continue
                        try:
                            if field_type == "adjustment_click":
                                # Use merged_json value for adjustment_click
                                adj_click(self.driver, value, xpath, mode)

                            else:    

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


# def upload_mls_for_order(self, order_id: int) -> bool:
#     # Fetch order data
#     data = fetch_upload_data(self, order_id)
#     if not data:
#         update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
#         return False

#     # Get MLS document info
#     mls_doc = next((d for d in data.get("documents", []) if d.get("type", "").lower()== "mls"), None)
#     if not mls_doc:
#         print(f"[WARN] No MLS document found for order {order_id}")
#         return True
#         #return False

#     file_path = mls_doc.get("path")
#     if not file_path or not os.path.exists(file_path):
#         print(f"[ERROR] MLS file not found: {file_path}")
#         return False

#     try:
#         # Upload MLS file
#         input_elem = self.driver.find_element(By.ID, "fname_MLS")
#         self.driver.execute_script("""
#             arguments[0].style.display = 'block';
#             arguments[0].style.visibility = 'visible';
#         """, input_elem)
#         input_elem.send_keys(file_path)
#         print(f"[INFO] MLS uploaded: {file_path}")
#         time.sleep(10)
#         single_source_save_form(self.driver)
#         # Verify that the file is uploaded
#         # Step 2: Wait until the uploaded file appears in the table
#         try:
#             uploaded_file = WebDriverWait(self.driver, 10).until(
#                 EC.presence_of_element_located((By.XPATH, "//a[contains(@class,'business_text') and contains(text(),'.pdf')]"))
#             )
#             print(f"File uploaded successfully: {uploaded_file.text}")
#             return True
#         except:
#             print("File upload verification failed.")
#             return False

#     except Exception as e:
#         print(f"[ERROR] Failed to upload MLS: {e}")
#         return False

def upload_mls_for_order(self, order_id: int) -> bool:
    """
    Uploads MLS file after removing any existing ones.
    """
    try:
        # Step 0: Ensure we are in _MAIN frame and clear overlays
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame("_MAIN")
        close_validation_popup(self.driver)

        # Fetch order data
        data = fetch_upload_data(self, order_id)
        if not data:
            update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed", hybrid_token)
            return False

        # Get MLS document info
        mls_doc = next(
            (d for d in data.get("documents", []) if d.get("type", "").lower() == "mls"),
            None
        )

        if not mls_doc:
            print(f"[WARN] No MLS document found for order {order_id}")
            return True

        file_path = mls_doc.get("path")
        if not file_path or not os.path.exists(file_path):
            print(f"[ERROR] MLS file not found: {file_path}")
            return False

        # -------------------------------------------------
        # STEP 1: Remove ANY existing MLS files (Multiple)
        # -------------------------------------------------
        print("[INFO] Checking for existing MLS files to remove...")
        files_to_remove = []
        
        # 1. Identify checkboxes in the MLS cell specifically
        try:
            # The input is id="fname_MLS". We look for checkboxes in its parent td.
            mls_row_cell = self.driver.find_element(By.ID, "fname_MLS").find_element(By.XPATH, "./ancestor::td[1]/following-sibling::td[1]")
            mls_cell_checkboxes = mls_row_cell.find_elements(By.XPATH, ".//input[@type='checkbox' and @name='remove_file']")
            for cb in mls_cell_checkboxes:
                if cb not in files_to_remove:
                    files_to_remove.append(cb)
                    print(f"[INFO] Found targeted MLS removal box: {cb.get_attribute('value')}")
        except Exception as e:
            print(f"[WARN] Error finding targeted MLS cell boxes: {e}")

        # 2. Identify any other checkboxes on the page where filename starts with 'mls'
        try:
            all_remove_boxes = self.driver.find_elements(By.XPATH, "//input[@name='remove_file']")
            for cb in all_remove_boxes:
                filename = (cb.get_attribute("value") or "").lower()
                if filename.startswith("mls") and filename.endswith(".pdf"):
                    if cb not in files_to_remove:
                        files_to_remove.append(cb)
                        print(f"[INFO] Found global MLS removal box: {cb.get_attribute('value')}")
        except:
            pass

        # 3. Mark all identified for removal
        if files_to_remove:
            print(f"[INFO] Removing {len(files_to_remove)} existing MLS file(s)...")
            marked_count = 0
            for box in files_to_remove:
                # Use robust JS marking
                is_checked = self.driver.execute_script("return arguments[0].checked;", box)
                if not is_checked:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", box)
                    self.driver.execute_script("""
                        var el = arguments[0];
                        el.checked = true;
                        el.click(); // Trigger portal JS
                        el.checked = true; // Stay checked
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                    """, box)
                    marked_count += 1

            if marked_count > 0:
                single_source_save_form(self.driver)
                # Re-ensure frame after save
                self.driver.switch_to.default_content()
                self.driver.switch_to.frame("_MAIN")
                print(f"[SUCCESS] {marked_count} MLS files marked for removal and form saved.")
            else:
                print("[INFO] All detected MLS files were already marked.")
        else:
            print("[INFO] No existing MLS files detected for removal.")

        # -------------------------------------------------
        # STEP 2: Upload MLS file
        # -------------------------------------------------
        print(f"[INFO] Uploading new MLS file: {file_path}")
        input_elem = self.driver.find_element(By.ID, "fname_MLS")
        self.driver.execute_script("""
            arguments[0].style.display = 'block';
            arguments[0].style.visibility = 'visible';
        """, input_elem)

        input_elem.send_keys(file_path)
        print(f"[INFO] MLS uploaded: {file_path}")

        single_source_save_form(self.driver)

        # -------------------------------------------------
        # STEP 3: VERIFY MLS UPLOAD
        # -------------------------------------------------
        # Re-verify by looking for the remove checkbox again next to the input
        def mls_uploaded(driver):
            try:
                elem = driver.find_element(By.ID, "fname_MLS")
                remove_checkbox = elem.find_element(By.XPATH, "./ancestor::tr//input[@type='checkbox' and @name='remove_file']")
                return remove_checkbox.is_displayed()
            except:
                return False

        WebDriverWait(self.driver, 15).until(mls_uploaded)

        print("[SUCCESS] MLS upload verified successfully")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to upload MLS: {e}")
        return False



# def upload_tax_for_order(self, order_id: int, wait_seconds: int = 10) -> bool:
#     """
#     Uploads the Tax file for a given order and verifies it appears as 'Tax Sheet' in Photos section.

#     Args:
#         order_id (int): The order ID.
#         wait_seconds (int): Max seconds to wait for the uploaded file to appear.

#     Returns:
#         bool: True if upload and verification succeeded, False otherwise.
#     """
#     # Fetch order data
#     data = fetch_upload_data(self, order_id)
#     if not data:
#         update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
#         print(f"[ERROR] No data found for order {order_id}")
#         return False

#     # Get Tax document info
#     tax_doc = next((d for d in data.get("documents", []) if d.get("type", "").lower() == "tax"), None)
#     if not tax_doc:
#         print(f"[WARN] No Tax document found for order {order_id}")
#         return True
#         #return False

#     file_path = tax_doc.get("path")
#     if not file_path or not os.path.exists(file_path):
#         print(f"[ERROR] Tax file not found: {file_path}")
#         return False

#     try:
#         # Upload Tax file
#         file_input = self.driver.find_element(By.ID, "fname_Photos")
#         self.driver.execute_script("""
#             arguments[0].style.display = 'block';
#             arguments[0].style.visibility = 'visible';
#         """, file_input)
#         file_input.send_keys(file_path)

#         # Set Type = "Other"
#         type_select = self.driver.find_element(By.ID, "fname_Photos_Type")
#         for option in type_select.find_elements(By.TAG_NAME, "option"):
#             if option.text.strip() == "Subject":
#                 option.click()
#                 break

#         # Set Description = "Tax Sheet"
#         desc_select = self.driver.find_element(By.ID, "fname_Photos_Description")
#         for option in desc_select.find_elements(By.TAG_NAME, "option"):
#             if option.text.strip() == "Tax Sheet":
#                 option.click()
#                 break
#         time.sleep(10)    
#         single_source_save_form(self.driver)        
#         print(f"[INFO] Tax file uploaded: {file_path}")
    
#         # Wait for the uploaded file to appear in the portal
#         # --- Verification ---
#         try:
#             uploaded_file_elem = WebDriverWait(self.driver, wait_seconds).until(
#                 EC.visibility_of_element_located(
#                     (By.XPATH, f"//input[@value='Subject Tax Sheet']")
#                 )
#             )
#             if uploaded_file_elem:
#                 print(f"[SUCCESS] Tax file confirmed uploaded for order {order_id}")
#                 return True
#         except:
#             print(f"[ERROR] Tax file not visible on portal after upload for order {order_id}")
#             return False

#     except Exception as e:
#         print(f"[ERROR] Failed to upload Tax: {e}")
#         return False

def remove_all_subject_tax_sheets(self):
    """
    Removes all existing files with Description 'Subject Tax Sheet'.
    Uses JS logic for state verification to avoid false positives.
    """
    try:
        # Step 0: Clear any blocking popups/modals in current frame
        close_validation_popup(self.driver)

        # Find all Description inputs with value 'Subject Tax Sheet'
        # Using normalize-space to handle potential trailing spaces
        tax_description_xpath = "//input[contains(@id,'@Description') and contains(normalize-space(@value), 'Subject Tax Sheet')]"
        tax_description_inputs = self.driver.find_elements(By.XPATH, tax_description_xpath)

        if not tax_description_inputs:
            print("[INFO] No existing Subject Tax Sheet found")
            return

        print(f"[INFO] Found {len(tax_description_inputs)} Subject Tax Sheet(s). Removing...")

        files_marked_for_removal = 0
        for description_input in tax_description_inputs:
            try:
                # 1. Extract the file index (e.g., 'Photos4') from the input ID or Name
                # Example ID: PS_FORM/FILES/File[.='Photos4']/@Description
                element_id = description_input.get_attribute("id") or ""
                element_name = description_input.get_attribute("name") or ""
                
                index_match = re.search(r"File\[\.='(.*?)'\]", element_id + element_name)
                remove_checkbox = None
                
                if index_match:
                    index = index_match.group(1)
                    # 2. Find the specific checkbox where value contains this index
                    try:
                        remove_checkbox = self.driver.find_element(
                            By.XPATH, f"//input[@name='remove_file' and contains(@value, '{index}')]"
                        )
                    except:
                        pass

                if not remove_checkbox:
                    # Fallback to the broad search if index matching fails
                    remove_checkbox = description_input.find_element(
                        By.XPATH, "./ancestor::tr//input[@type='checkbox' and @name='remove_file']"
                    )
                
                # Check real state via JS
                is_checked = self.driver.execute_script("return arguments[0].checked;", remove_checkbox)
                
                if not is_checked:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", remove_checkbox)
                    
                    # Force check and trigger events
                    self.driver.execute_script("""
                        var el = arguments[0];
                        el.checked = true;
                        el.click(); // Click to trigger portal's internal JS
                        el.checked = true; // Ensure it stays checked
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                    """, remove_checkbox)
                    
                    # Double check state
                    if self.driver.execute_script("return arguments[0].checked;", remove_checkbox):
                        files_marked_for_removal += 1
                        print(f"[INFO] Marked for removal: {description_input.get_attribute('value')}")
                    else:
                        print(f"[WARN] Failed to mark checkbox for: {description_input.get_attribute('value')}")
                else:
                    files_marked_for_removal += 1
                    print(f"[INFO] Already marked for removal: {description_input.get_attribute('value')}")

            except Exception as e:
                print(f"[WARN] Error marking removal for an entry: {e}")
                continue

        if files_marked_for_removal > 0:
            print(f"[INFO] Saving form to apply {files_marked_for_removal} removals...")
            single_source_save_form(self.driver)

            # CRITICAL: Re-ensure we are in _MAIN after save/reload
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame("_MAIN")

            # Wait until all Subject Tax Sheets are removed
            try:
                WebDriverWait(self.driver, 20).until_not(
                    EC.presence_of_element_located((By.XPATH, tax_description_xpath))
                )
                print("[SUCCESS] All Subject Tax Sheets removed successfully")
            except Exception as e:
                print(f"[ERROR] Timeout waiting for Subject Tax Sheet removal. They might still be there: {e}")
        else:
            print("[INFO] No sheets were marked for removal.")

    except Exception as e:
        print(f"[ERROR] Failed in remove_all_subject_tax_sheets: {e}")


def upload_tax_for_order(self, order_id: int, wait_seconds: int = 30) -> bool:
    """
    Uploads the Tax file for a given order after removing any existing 'Subject Tax Sheet'.
    Uses multiple frame-re-ensures and explicit waits to handle portal instability.
    """
    try:
        # Step 1: Framework and Data Preparation
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame("_MAIN")
        close_validation_popup(self.driver)

        data = fetch_upload_data(self, order_id)
        if not data:
            print(f"[ERROR] No upload data found for order {order_id}")
            return False

        tax_doc = next(
            (d for d in data.get("documents", []) if d.get("type", "").lower() == "tax"),
            None
        )
        if not tax_doc:
            print(f"[WARN] No Tax document found for order {order_id}")
            return True

        file_path = tax_doc.get("path")
        if not file_path or not os.path.exists(file_path):
            print(f"[ERROR] Tax file not found: {file_path}")
            return False

        # Step 2: Clear old sheets
        print("[INFO] Starting removal phase...")
        remove_all_subject_tax_sheets(self)

        # Step 3: Performance Upload
        # Syncing frame state again
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame("_MAIN")
        
        print(f"[INFO] Preparing to upload new Tax Sheet: {file_path}")
        try:
            file_input = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "fname_Photos"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", file_input)
            
            # Use JS to reveal if hidden, but send_keys normally
            self.driver.execute_script("arguments[0].style.display='block'; arguments[0].style.visibility='visible';", file_input)
            file_input.send_keys(file_path)
            time.sleep(3) # Wait for file to register with browser
            
            # Select Type = Subject
            select_field(self.driver, "Subject", "fname_Photos_Type", "id")
            time.sleep(1)
            
            # Select Description = Tax Sheet
            select_field(self.driver, "Tax Sheet", "fname_Photos_Description", "id")
            time.sleep(2)
            
            # Last check: verify the Type/Description values stuck
            type_val = self.driver.execute_script("return document.getElementById('fname_Photos_Type').value;")
            desc_val = self.driver.execute_script("return document.getElementById('fname_Photos_Description').value;")
            print(f"[INFO] Selected Type: {type_val}, Description: {desc_val}")

            # Save the form
            print("[INFO] Clicking Save for Tax Sheet upload...")
            single_source_save_form(self.driver)
            
        except Exception as e:
            print(f"[ERROR] Interaction failure during Tax upload: {e}")
            return False

        # Step 4: Verification
        print("[INFO] Verifying upload success...")
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame("_MAIN")
        
        tax_description_xpath = "//input[contains(@id,'@Description') and contains(normalize-space(@value), 'Subject Tax Sheet')]"
        try:
            WebDriverWait(self.driver, wait_seconds).until(
                EC.presence_of_element_located((By.XPATH, tax_description_xpath))
            )
            print(f"[SUCCESS] Subject Tax Sheet verified for order {order_id}")
            return True
        except Exception as e:
            print(f"[ERROR] Verification failed for Subject Tax Sheet after upload attempt: {e}")
            # Log what we see instead
            all_descriptions = self.driver.find_elements(By.XPATH, "//input[contains(@id,'@Description')]")
            print(f"[DEBUG] Found {len(all_descriptions)} total descriptions on page.")
            for d in all_descriptions:
                print(f"[DEBUG] Description ID: {d.get_attribute('id')}, Value: {d.get_attribute('value')}")
            return False

    except Exception as e:
        print(f"[ERROR] Critical failure in upload_tax_for_order: {e}")
        return False


# def upload_tax_for_order(self, order_id: int, wait_seconds: int = 15) -> bool:
#     """
#     Removes ALL existing Subject Tax Sheets (single save),
#     then uploads the new Tax Sheet.
#     """

#     try:
#         wait = WebDriverWait(self.driver, wait_seconds)

#         # =====================================================
#         # STEP 1: REMOVE ALL SUBJECT TAX SHEETS
#         # =====================================================
#         subject_tax_inputs = self.driver.find_elements(
#             By.XPATH,
#             "//input[@type='text' and normalize-space(@value)='Subject Tax Sheet']"
#         )

#         if subject_tax_inputs:
#             print(f"[INFO] Found {len(subject_tax_inputs)} Subject Tax Sheets")

#             for desc_input in subject_tax_inputs:
#                 try:
#                     remove_checkbox = desc_input.find_element(
#                         By.XPATH,
#                         ".//following::input[@type='checkbox' and @name='remove_file'][1]"
#                     )

#                     if not remove_checkbox.is_selected():
#                         self.driver.execute_script(
#                             "arguments[0].scrollIntoView({block:'center'});",
#                             remove_checkbox
#                         )
#                         self.driver.execute_script(
#                             "arguments[0].click();", remove_checkbox
#                         )

#                 except Exception as e:
#                     print(f"[WARN] Could not select one remove checkbox: {e}")

#             # ✅ SINGLE SAVE
#             single_source_save_form(self.driver)

#             # Wait until all Subject Tax Sheets are gone
#             wait.until(
#                 EC.invisibility_of_element_located(
#                     (By.XPATH,
#                      "//input[@type='text' and normalize-space(@value)='Subject Tax Sheet']")
#                 )
#             )

#             print("[SUCCESS] All existing Subject Tax Sheets removed")

#         else:
#             print("[INFO] No existing Subject Tax Sheets found")

#         # =====================================================
#         # STEP 2: UPLOAD NEW TAX SHEET
#         # =====================================================
#         data = fetch_upload_data(self, order_id)
#         tax_doc = next(
#             (d for d in data.get("documents", [])
#              if d.get("type", "").lower() == "tax"),
#             None
#         )

#         if not tax_doc:
#             print("[WARN] No Tax document found")
#             return True

#         file_path = tax_doc.get("path")
#         if not file_path or not os.path.exists(file_path):
#             print(f"[ERROR] Tax file missing: {file_path}")
#             return False

#         file_input = self.driver.find_element(By.ID, "fname_Photos")
#         self.driver.execute_script(
#             "arguments[0].style.display='block'; arguments[0].style.visibility='visible';",
#             file_input
#         )
#         file_input.send_keys(file_path)

#         # Set Type = Subject
#         for opt in self.driver.find_element(
#             By.ID, "fname_Photos_Type"
#         ).find_elements(By.TAG_NAME, "option"):
#             if opt.text.strip() == "Subject":
#                 opt.click()
#                 break

#         # Set Description = Tax Sheet
#         for opt in self.driver.find_element(
#             By.ID, "fname_Photos_Description"
#         ).find_elements(By.TAG_NAME, "option"):
#             if opt.text.strip() == "Tax Sheet":
#                 opt.click()
#                 break

#         time.sleep(2)
#         single_source_save_form(self.driver)

#         # Wait for the uploaded file to appear in the portal
#         # --- Verification ---
#         try:
#             uploaded_file_elem = WebDriverWait(self.driver, wait_seconds).until(
#                 EC.visibility_of_element_located(
#                     (By.XPATH, f"//input[@value='Subject Tax Sheet']")
#                 )
#             )
#             if uploaded_file_elem:
#                 print(f"[SUCCESS] Tax file confirmed uploaded for order {order_id}")
#                 return True
#         except:
#             print(f"[ERROR] Tax file not visible on portal after upload for order {order_id}")
#             return False

#     except Exception as e:
#         print(f"[ERROR] Failed to upload Tax: {e}")
#         return False


# 
def remove_existing_comparable_photos(self):
    """
    Removes all existing Listing 1-3 and Sale 1-3 photos using index-based isolation.
    """
    try:
        # Step 0: Ensure correct frame and clear blocking popups
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame("_MAIN")
        close_validation_popup(self.driver)

        # Find all Description inputs that match Listing or Sale
        # Using normalize-space to handle variations in whitespace
        photo_desc_xpath = "//input[contains(@id,'@Description') and (contains(normalize-space(@value),'Listing') or contains(normalize-space(@value),'Sale'))]"
        photo_desc_inputs = self.driver.find_elements(By.XPATH, photo_desc_xpath)

        if not photo_desc_inputs:
            print("[INFO] No existing Listing/Sale photos found.")
            return

        print(f"[INFO] Found {len(photo_desc_inputs)} existing photos. Identifying checkboxes...")

        files_marked_for_removal = 0
        for desc_input in photo_desc_inputs:
            try:
                # 1. Extract file index (e.g. Photos6) from input metadata
                element_id = desc_input.get_attribute("id") or ""
                element_name = desc_input.get_attribute("name") or ""
                
                index_match = re.search(r"File\[\.='(.*?)'\]", element_id + element_name)
                remove_checkbox = None
                
                if index_match:
                    index = index_match.group(1)
                    # 2. Precise match for checkbox by index
                    try:
                        remove_checkbox = self.driver.find_element(
                            By.XPATH, f"//input[@name='remove_file' and contains(@value, '{index}')]"
                        )
                    except:
                        pass
                
                if not remove_checkbox:
                    # Fallback to ancestor search
                    remove_checkbox = desc_input.find_element(
                        By.XPATH, "./ancestor::tr//input[@type='checkbox' and @name='remove_file']"
                    )

                # 3. Check and Force removal state via JS
                is_checked = self.driver.execute_script("return arguments[0].checked;", remove_checkbox)
                
                if not is_checked:
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", remove_checkbox)
                    self.driver.execute_script("""
                        var el = arguments[0];
                        el.checked = true;
                        el.click(); // Trigger portal JS
                        el.checked = true; // Stay checked
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                    """, remove_checkbox)
                    
                    if self.driver.execute_script("return arguments[0].checked;", remove_checkbox):
                        files_marked_for_removal += 1
                        print(f"[INFO] Marked for removal: {desc_input.get_attribute('value')}")
                else:
                    files_marked_for_removal += 1
                    print(f"[INFO] Already marked for removal: {desc_input.get_attribute('value')}")

            except Exception as e:
                print(f"[WARN] Failed to mark removal for {desc_input.get_attribute('value')}: {e}")
                continue

        if files_marked_for_removal > 0:
            print(f"[INFO] Saving form to apply {files_marked_for_removal} removals...")
            single_source_save_form(self.driver)
            
            # Re-ensure frame after save
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame("_MAIN")
            
            try:
                WebDriverWait(self.driver, 15).until_not(
                    EC.presence_of_element_located((By.XPATH, photo_desc_xpath))
                )
                print("[SUCCESS] All existing Listing/Sale photos removed.")
            except:
                print("[WARN] Some photos might still be visible after removal attempt.")
        else:
            print("[INFO] No photos were marked for removal.")

    except Exception as e:
        print(f"[ERROR] Critical failure in remove_existing_comparable_photos: {e}")


def upload_photos_to_order(self, comparables_folder):
    """
    Uploads Listing 1-3 and Sale 1-3 photos dynamically after removing any existing ones.
    Verifies all expected photos after upload.
    """
    try:
        # Step 0: Initial frame setup
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame("_MAIN")
        close_validation_popup(self.driver)

        if not os.path.exists(comparables_folder):
            print("⚠ Comparables folder missing.")
            return False

        # Step 1: Remove any existing Listing/Sale photos
        remove_existing_comparable_photos(self)

        # Re-ensure frame after removal sequence
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame("_MAIN")
        
        # Step 2: Map filenames to input IDs
        files_to_upload = {}
        for fname in os.listdir(comparables_folder):
            if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            match = re.match(r'([as])([1-3])\.(jpg|jpeg|png)', fname, flags=re.IGNORECASE)
            if match:
                prefix, idx, _ = match.groups()
                input_id = f"fname_Listing{idx}_Front" if prefix.lower() == 'a' else f"fname_Sale{idx}_Front"
                files_to_upload[fname] = input_id

        if not files_to_upload:
            print("⚠ No matching Listing or Sale photos found in folder.")
            return False

        # Step 3: Upload photos
        uploaded_photos = {}
        for fname, input_id in files_to_upload.items():
            file_path = os.path.join(comparables_folder, fname)
            try:
                # Ensure we are in frame before each upload
                self.driver.switch_to.default_content()
                self.driver.switch_to.frame("_MAIN")
                
                file_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, input_id))
                )
                # Ensure input is visible
                self.driver.execute_script("arguments[0].style.display='block'; arguments[0].style.visibility='visible';", file_input)
                
                file_input.send_keys(file_path)
                print(f"[INFO] Uploaded {fname} → {input_id}")
                uploaded_photos[fname] = True
                time.sleep(1) # Extra stability
            except Exception as e:
                print(f"[ERROR] Failed to upload {fname} → {input_id}: {e}")
                uploaded_photos[fname] = False

        single_source_save_form(self.driver)

        # Re-ensure frame after final save
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame("_MAIN")

        # Step 4: Verification
        all_uploaded = True
        max_wait = 15  # seconds
        poll_interval = 2  # seconds

        for fname, input_id in files_to_upload.items():
            verified = False
            elapsed = 0
            while elapsed < max_wait:
                try:
                    # Check for the removal checkbox appearing next to the ID (indicates successful upload)
                    v_xpath = f"//input[@id='{input_id}']/ancestor::tr//input[@type='checkbox' and @name='remove_file']"
                    checkbox = self.driver.find_element(By.XPATH, v_xpath)
                    if checkbox.is_displayed():
                        print(f"[SUCCESS] Verified uploaded: {fname}")
                        verified = True
                        break
                except:
                    pass
                time.sleep(poll_interval)
                elapsed += poll_interval

            if not verified:
                print(f"[ERROR] Verification failed for: {fname}")
                all_uploaded = False

        if all_uploaded:
            print("[SUCCESS] All Listing and Sale photos uploaded and verified.")
        else:
            print("[WARN] Some photos failed verification.")
        
        return all_uploaded

    except Exception as e:
        print(f"[ERROR] Critical failure in upload_photos_to_order: {e}")
        return False
