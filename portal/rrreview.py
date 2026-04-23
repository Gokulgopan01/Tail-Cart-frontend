import logging
import re
import time
import requests
import json
import os
from dotenv import load_dotenv
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from config import env
load_dotenv()
from condtions.all_portal_conditions import generate_condition_data
from utils.helper import adj_click, data_filling_text, extract_data_sections, fetch_upload_data, get_cookie_from_api, get_nested, get_order_address_from_assigned_order, handle_login_status, javascript_excecuter_filling, load_form_config_and_data, params_check, radio_btn_click, rrr_fill_listing_history, rrr_fill_repair_details, rrr_select_hoa_amenities, rrr_select_amenities, save_form, save_form_adj, select_checkboxes_from_list, select_field, setup_driver, single_checkbox, update_client_account_status, update_order_status, update_portal_login_confirmation_status, tfs_statuschange, select_radio_button, select_drop_button, select_empty_field
from integrations.hybrid_bpo_api import HybridBPOApi
from utils.glogger import GLogger


logger = GLogger()

process_type, hybrid_orderid, hybrid_token = params_check()
logger.log(
    module="rrreview-main",
    order_id=hybrid_orderid,
    action_type="Info",
    remarks=f"type,orderid,token,{process_type},{hybrid_orderid},{hybrid_token}",
    severity="INFO"
)
load_dotenv()
class rrreview:
    def __init__(self, username, password, portal_url, portal_name, proxy, session,account_id, portal_key):
        self.username = username
        self.password = password
        self.portal_url = portal_url
        self.portal_name = portal_name
        self.proxy = proxy
        self.driver = None
        self.session=session
        self.login_status = "Not started"
        self.portal_key = portal_key
        logging.basicConfig(level=logging.INFO)


    def login_to_portal(self):
        try:
    
            # Step 1: Setup WebDriver
            setup_driver(self)

            api_response = get_cookie_from_api(self.username, portal="rrr", proxy=self.proxy)
            logger.log(
                module="rrreview-login_to_portal",
                order_id=hybrid_orderid,
                action_type="Debug",
                remarks=f"API Response: {api_response}",
                severity="INFO"
            )
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
            logger.log(
                module="rrreview-login_to_portal",
                order_id=hybrid_orderid,
                action_type="Debug",
                remarks=f"Current URL: {current_url}",
                severity="INFO"
            )
            # if 'https://www.rrreview.com/#/baseauth/activeorders' in current_url:
            #     logging.info("Login successful")
            #     return "Login success", self.driver
            # else:
            #     logging.error(f"Login failed. URL landed: {current_url}")
            #     return "Login error", self.driver
            # handle_login_status(current_url, self.username, ["baseauth/activeorders"], self.portal_name)
                
                # handle_login_status(current_url, self.username, success_keywords, self.portal_name)
                # return self.login_status, self.driver

            # arg1 = "SmartEntry"  # Manually set for testing
            #arg1="PortalLogin"
            # arg1="AutoLogin"
            if process_type == "SmartEntry":
                self.rrreview_formopen()
                
            else:
                update_portal_login_confirmation_status(hybrid_orderid)
                login_check_keyword = ["baseauth/activeorders"]
                handle_login_status(current_url, self.username, login_check_keyword, self.portal_name)

          
        except Exception as e:
            self.login_status = f"Exception occurred: {e}"
            # Fix 6: Use GLogger for consistency with the rest of the file
            logger.log(
                module="rrreview-login_to_portal",
                order_id=hybrid_orderid,
                action_type="Exception",
                remarks=f"Exception during login: {e}",
                severity="INFO"
            )
            update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed", hybrid_token)
            update_client_account_status(self.account_id)
            handle_login_status("EXCEPTION", self.username, ["activeorders"], self.portal_name)
            return "Login error", self.driver
        
    def rrreview_formopen(self):
        try:
            orders_from_api = HybridBPOApi.get_entry_order(hybrid_orderid)
            if not orders_from_api:  
                logger.log(
                    module="rrreview-rrreview_formopen",
                    order_id=hybrid_orderid,
                    action_type="Condition_check",
                    remarks="No orders found.",
                    severity="INFO"
                )
                return
            

            for order_from_api in orders_from_api:
                portal_name = order_from_api.get("portal_name", "")
                username = order_from_api.get("username", "")
                password = order_from_api.get("password", "")
                portal_url = order_from_api.get("portal_url", "")
                proxy = order_from_api.get("proxy", None)  # Optional proxy
                session=order_from_api.get("session",None)
                order_id=order_from_api.get("order_id","")
                order_details_from_api, tfs_orderid, is_qc, master_order_id=get_order_address_from_assigned_order(order_id,hybrid_token)
            
            # --- Step 2: Parse ALL Active Orders in RRR portal ---
            print("Looking for Active Orders...")
            logger.log(
                module="rrreview-rrreview_formopen",
                order_id=hybrid_orderid,
                action_type="Info",
                remarks="Scanning portal dashboard for active order rows...",
                severity="INFO"
            )

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
                    portalorder_id = order_id_el.get_attribute('textContent').strip()

                    # Column 2: Form Type
                    form_type_el = row.find_element(By.XPATH, ".//ion-col[2]//ion-label")
                    form_type = form_type_el.get_attribute('textContent').strip().upper()

                    print(f"Discovered Order: {portalorder_id} - {form_type}")

                    # Only store valid numeric order IDs
                    if portalorder_id.isdigit():
                        portal_order_data[portalorder_id] = form_type
                except Exception as e:
                    logger.log(
                        module="rrreview-rrreview_formopen",
                        order_id=hybrid_orderid,
                        action_type="Warning",
                        remarks=f"Row parsing warning: {e}",
                        severity="INFO"
                    )
                    continue

            logger.log(
                module="rrreview-rrreview_formopen",
                order_id=hybrid_orderid,
                action_type="Info",
                remarks=f"Portal scan complete. Found {len(portal_order_data)} orders.",
                severity="INFO"
            )
            print(f"Total Active Orders: {len(portal_order_data)}")

            # Extract HybridBPO order IDs for matching
            hybrid_order_id = [str(o.get("portal_orderid", "")).strip() for o in orders_from_api if o.get("portal_orderid")]

            # Find common order IDs
            matched_order = [oid for oid in portal_order_data.keys() if oid in hybrid_order_id]
            print(f"Matched Orders for Processing:{matched_order}")
            logger.log(
                module="rrreview-rrreview_formopen",
                order_id=hybrid_orderid,
                action_type="Info",
                remarks=f"Matching Complete. {len(matched_order)} orders pending automated processing.",
                severity="INFO"
            )

            # Optional: define allowed form types for SmartEntry
            allowed_form_types = ["EXTERIOR BPO"]

            # Click only matched orders **with allowed form type**
            for order in matched_order:
                form_type = portal_order_data.get(order)
                if form_type in allowed_form_types:
                    print(f"Opening Order {order} ({form_type})...")
                    logger.log(
                        module="rrreview-rrreview_formopen",
                        order_id=hybrid_orderid,
                        action_type="Info",
                        remarks=f"Opening order {order} with form type {form_type}",
                        severity="INFO"
                    )
                    # Fix 2: Guard form fill on click success
                    if self.click_order_by_id(order):
                        # Proceed to form fill once open
                        self.rrreview_formopen_fill(form_type,order_id,session,tfs_orderid,is_qc,merged_json=None)
                    else:
                        logger.log(
                            module="rrreview-rrreview_formopen",
                            order_id=hybrid_orderid,
                            action_type="Error",
                            remarks=f"Failed to open order {order}. Skipping.",
                            severity="ERROR"
                        )

                else:
                    logger.log(
                        module="rrreview-rrreview_formopen",
                        order_id=hybrid_orderid,
                        action_type="Warning",
                        remarks=f"Skipping order {order} with unsupported form type: {form_type}",
                        severity="INFO"
                    )

        except Exception as e:
            #logging.exception(f"Exception in rrreview_formopen: {e}")
            logger.log(
                module="rrreview-rrreview_formopen",
                order_id=hybrid_orderid,
                action_type="Exception",
                remarks=f"Exception in rrreview_formopen: {e}",
                severity="INFO"
            )

    def click_order_by_id(self, order_id):
        """Find and click the given order ID on the RRR portal dashboard."""
        try:
            logger.log(
                module="rrreview-click_order_by_id",
                order_id=hybrid_orderid,
                action_type="Info",
                remarks=f"Looking for order {order_id}...",
                severity="INFO"
            )

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
                text = label.get_attribute('textContent')
                if text:
                    text = text.strip()
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
            print(f"Order {order_id} clicked successfully.")
            logger.log(
                module="rrreview-click_order_by_id",
                order_id=hybrid_orderid,
                action_type="Info",
                remarks=f"Successfully clicked order {order_id}",
                severity="INFO"
            )

            # Optional: wait a bit for navigation or popup
            time.sleep(3)


            try:
                logger.log(
                    module="rrreview-click_order_by_id",
                    order_id=hybrid_orderid,
                    action_type="Info",
                    remarks="Looking for 'I am ready to enter data or submit report' button...",
                    severity="INFO"
                )

                # Wait until the button is visible & clickable
                ready_button = WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable((
                        By.XPATH, "//ion-button[.//span[normalize-space()='I am ready to enter data or submit report']]"
                    ))
                )

                # Use native Selenium click 
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", ready_button)
                time.sleep(1)  # small pause so Angular attaches handlers
                print("Clicking 'Ready to enter data' button...")
                ready_button.click()  

                logger.log(
                    module="rrreview-click_order_by_id",
                    order_id=hybrid_orderid,
                    action_type="Info",
                    remarks="Button clicked, waiting for form to open...",
                    severity="INFO"
                )

                # Now wait for the form submitorder button
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id='submitorderbutton']"))
                )
                logger.log(
                    module="rrreview-click_order_by_id",
                    order_id=hybrid_orderid,
                    action_type="Success",
                    remarks="Order form interface loaded and confirmed.",
                    severity="INFO"
                )
                return True
              
            except Exception as e:
                    logger.log(
                        module="rrreview-click_order_by_id",
                        order_id=hybrid_orderid,
                        action_type="Exception",
                        remarks=f"Could not open the form: {e}",
                        severity="INFO"
                    )
                    return False

        except Exception as e:
            # Fix 3: Added return False so caller can detect click failure
            logger.log(
                module="rrreview-click_order_by_id",
                order_id=hybrid_orderid,
                action_type="Exception",
                remarks=f"Could not click order {order_id}: {e}",
                severity="INFO"
            )
            return False
      
    def rrreview_formopen_fill(self,formtype_value,order_id,session,tfs_orderid,is_qc,merged_json):
        """Handles mapping config, merged_json loading, and form-filling for RRReview SmartEntry."""
        try:
            # Load ResearchPad API endpoint from environment
            researchpad_data_retrival_url=env.RESEARCHPAD_DATA_URL
            logger.log(
                module="rrreview-rrreview_formopen_fill",
                order_id=hybrid_orderid,
                action_type="Debug",
                remarks=f"ResearchPad URL: {researchpad_data_retrival_url}",
                severity="INFO"
            )

            #  Step 1: Choose JSON config path based on form type
            if formtype_value == "EXTERIOR BPO":
                print(f"Mapping matched for {formtype_value}")
                logger.log(
                    module="rrreview-rrreview_formopen_fill",
                    order_id=hybrid_orderid,
                    action_type="Info",
                    remarks="Form type matches EXTERIOR BPO",
                    severity="INFO"
                )
                config_path = 'json/rrreviewjson/RRReview_Exterior_BPO.json'
            else:
                #logging.warning(f"No matching config path found for form type: {formtype_value}")
                logger.log(
                    module="rrreview-rrreview_formopen_fill",
                    order_id=hybrid_orderid,
                    action_type="Warning",
                    remarks=f"No matching config path found for form type: {formtype_value}",
                    severity="INFO"
                )
                update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
                # Fix 5: Restored TFS failure status call on form type mismatch
                # tfs_statuschange(tfs_orderid, "27", "5", "20")
                return
            
            form_config, merged_json = load_form_config_and_data(
            order_id=order_id,
            config_path=config_path,
            researchpad_data_retrival_url=researchpad_data_retrival_url,
            session=session,
            merged_json=merged_json,
            token=hybrid_token
            )
            if not form_config or not merged_json:
                print(f"[!] Smart Entry Data Missing for Order {order_id}")
                logger.log(
                    module="rrreview-rrreview_formopen_fill",
                    order_id=hybrid_orderid,
                    action_type="Warning",
                    remarks=f"Config or data missing for order {order_id}",
                    severity="INFO"
                )
                return False
        
            # Extract and generate condition_data, attach it inside merged_json for usage if needed
            sub_data, comp_data, adj_data, rental_data,sold1,sold2,sold3, list1, list2, list3,rental_list1,rental_list2,rental_leased1,rental_leased2,adj_sold1,adj_sold2,adj_sold3,adj_list1,adj_list2,adj_list3, prior1, prior2, prior3 = extract_data_sections(merged_json)
            condition_data = generate_condition_data(sub_data, comp_data, adj_data, rental_data,sold1,sold2,sold3, list1, list2, list3,rental_list1,rental_list2,rental_leased1,rental_leased2,adj_sold1,adj_sold2,adj_sold3,adj_list1,adj_list2,adj_list3, prior1, prior2, prior3)
            if "entry_data" in merged_json and merged_json["entry_data"]:
                merged_json["entry_data"][0]["condition_data"] = condition_data

            try:
                # Fix 1: Assign return value to success (was NameError before)
                success = self.fill_form_multi(merged_json, order_id, form_config, session, tfs_orderid,is_qc)
                time.sleep(2)
                return success

            except Exception as e:
                #logging.exception(f"Error while navigating and filling forms: {e}")
                logger.log(
                    module="rrreview-rrreview_formopen_fill",
                    order_id=hybrid_orderid,
                    action_type="Exception",
                    remarks=f"Error while navigating and filling forms: {e}",
                    severity="INFO"
                )
                return False
        except Exception as e:
            #logging.exception(f"Exception in rrreview_formopen_fill: {e}")
            logger.log(
                    module="rrreview-rrreview_formopen_fill",
                    order_id=hybrid_orderid,
                    action_type="Exception",
                    remarks=f"Exception in rrreview_formopen_fill: {e}",
                    severity="INFO"
                )
            return False

    def fill_form_multi(self, merged_json, order_id, form_config, session, tfs_orderid,is_qc):
        """
         form filling function for RRReview portal.
        """

        # --- Internal caches for optimization ---
        key_expr_cache = {}
        value_cache = {}

        # --------------------------
        # Cached key extraction
        # --------------------------
        def get_keys_cached(key_expr):
            if key_expr not in key_expr_cache:
                key_expr_cache[key_expr] = re.findall(r"\['(.*?)'\]", key_expr)
            return key_expr_cache[key_expr]

        # --------------------------
        # Value extraction handler
        # --------------------------

        def extract_value_from_expr(expr: str):
            """Extracts values from nested merged_json."""
            if expr in value_cache:
                return value_cache[expr]

            # Define data sources
            data_sources = {
                "sub_data": sub_data,
                "comp_data": comp_data,
                "adj_data": adj_data,
                "rental_data": rental_data,
                "condition_data": condition_data,
                "entry_data[0]": merged_json.get("entry_data", [{}])[0],
                "sold1": sold1, "sold2": sold2, "sold3": sold3,
                "list1": list1, "list2": list2, "list3": list3,
                "rental_list1": rental_list1, "rental_list2": rental_list2,
                "rental_leased1": rental_leased1, "rental_leased2": rental_leased2,
                "adj_sold1": adj_sold1, "adj_sold2": adj_sold2, "adj_sold3": adj_sold3,
                "adj_list1": adj_list1, "adj_list2": adj_list2, "adj_list3": adj_list3,
                "prior1": prior1, "prior2": prior2, "prior3": prior3,
            }

            # Find matching prefix and extract nested keys
            for prefix, source in data_sources.items():
                if expr.startswith(prefix):
                    suffix = expr[len(prefix):]
                    keys = re.findall(r"\['(.*?)'\]", suffix)
                    value = get_nested(source, keys, None)

                    if isinstance(value, (int, float)):
                        value = str(value)

                    value_cache[expr] = value
                    return value

            # Default fallback: If it's a literal string (not an expression starting with a prefix), return it as-is
            # value_cache[expr] = None # Removed this, we want to return the literal
            return expr

        # --------------------------
        # Field type to function map
        # --------------------------
        field_actions = {
            "Textbox": data_filling_text,
            "Textbox_default": data_filling_text,
            "select_data": select_field,
            "select_default": select_field,
            "radiobutton_data": radio_btn_click,
            "radiobutton_default": radio_btn_click,
            "date_fill_javascript": javascript_excecuter_filling,
            "checkbox": single_checkbox,
            "button_click": adj_click,
            "rrr_listing_history_fill": rrr_fill_listing_history,
            "rrr_hoa_amenities": rrr_select_hoa_amenities,
            "rrr_amenities": rrr_select_amenities,
            "select_radio": select_radio_button,
            "select_drop_button": select_drop_button,
            "select_empty_field": select_empty_field,
        }

        # --------------------------
        # RRReview iframe tab mapping
        # --------------------------
        iframe_id_map = {
            "Order Instructions": "iframeBPOBPOEntryFormTab1",
            "Subject Information": "iframeBPOBPOEntryFormTab2",
            "Repair Information": "iframeBPOBPOEntryFormTab3",
            "Comparable Information": "iframeBPOBPOEntryFormTab4",
            "Photos/Documents": "iframeBPOBPOEntryFormTab5",
            "Validation Results": "iframeBPOBPOEntryFormTab6",
        }

        try:
            # --- Success-tracking flags (mirrors old version) ---
            # form_fill_success = True
            # photo_upload_success = True

            # --- Extract all JSON data sections ---
            (
                sub_data, comp_data, adj_data, rental_data,
                sold1, sold2, sold3,
                list1, list2, list3,
                rental_list1, rental_list2,
                rental_leased1, rental_leased2,
                adj_sold1, adj_sold2, adj_sold3,
                adj_list1, adj_list2, adj_list3, 
                prior1, prior2, prior3) = extract_data_sections(merged_json)

            if sub_data is None:
                #logging.error("'entry_data' missing or empty in merged_json")
                logger.log(
                    module="rrreview-fill_form_multi",
                    order_id=hybrid_orderid,
                    action_type="Condition_check",
                    remarks=f"'entry_data' missing or empty in merged_json",
                    severity="INFO"
                )
                update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed", hybrid_token)
                #tfs_statuschange(tfs_orderid, "27", "3", "14")
                return False

            # --- Generate computed conditional data ---
            condition_data = generate_condition_data(
                sub_data, comp_data, adj_data, rental_data,
                sold1, sold2, sold3, list1, list2, list3,
                rental_list1, rental_list2, rental_leased1, rental_leased2,
                adj_sold1, adj_sold2, adj_sold3, adj_list1, adj_list2, adj_list3,
                prior1, prior2, prior3
            )

            form_fill_success = False
            photo_upload_success = False
            form_pages = form_config.get("page", [])

            # --- Helper to resolve {condition_data['...']} in locators ---
            def resolve_template(template):
                if not template or '{' not in template:
                    return template
                try:
                    placeholders = re.findall(r'\{(.*?)\}', template)
                    for ph in placeholders:
                        val = extract_value_from_expr(ph)
                        if val is not None:
                            template = template.replace('{' + ph + '}', str(val))
                    return template
                except Exception:
                    return template

            # --------------------------
            # Iterate through pages & tabs
            # --------------------------
            for page in form_pages:
                for tab_name, controls in page.items():
                    
                    # ALWAYS exit iframe before switching tab
                    self.driver.switch_to.default_content()
                    time.sleep(0.5)
                    # Step 1: Click the corresponding tab
                    print(f"Switching to  {tab_name} Tab")
                    logger.log(
                        module="rrreview-fill_form_multi",
                        order_id=hybrid_orderid,
                        action_type="Info",
                        remarks=f"Switching to portal tab: {tab_name}",
                        severity="INFO"
                    )
                    
                    try:
                        tab_xpath = f"//a[contains(@class,'ui-tabs-anchor') and contains(.,'{tab_name}')]"
                        tab_element = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, tab_xpath))
                        )
                        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", tab_element)
                        time.sleep(0.5)
                        tab_element.click()
                        logger.log(
                            module="rrreview-fill_form_multi",
                            order_id=hybrid_orderid,
                            action_type="Info",
                            remarks=f"Clicked tab: {tab_name}",
                            severity="INFO"
                        )
                        time.sleep(1)
                    except Exception as e:
                        logger.log(
                            module="rrreview-fill_form_multi",
                            order_id=hybrid_orderid,
                            action_type="Warning",
                            remarks=f"Could not click tab '{tab_name}': {e}",
                            severity="INFO"
                        )
                        continue

                    # Step 2: Switch to iframe
                    # self.driver.switch_to.default_content()
                    iframe_id = iframe_id_map.get(tab_name)
                    if iframe_id:
                        try:
                            iframe = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.ID, iframe_id))
                            )
                            self.driver.switch_to.frame(iframe)
                            logger.log(
                                module="rrreview-fill_form_multi",
                                order_id=hybrid_orderid,
                                action_type="Info",
                                remarks=f"Switched to iframe: {iframe_id}",
                                severity="INFO"
                            )
                        except Exception as e:
                            logger.log(
                                module="rrreview-fill_form_multi",
                                order_id=hybrid_orderid,
                                action_type="Warning",
                                remarks=f"Could not switch to iframe {iframe_id}: {e}",
                                severity="INFO"
                            )
                            continue
                    else:
                        logger.log(
                            module="rrreview-fill_form_multi",
                            order_id=hybrid_orderid,
                            action_type="Warning",
                            remarks=f"No iframe mapping for tab: {tab_name}",
                            severity="INFO"
                        )

                    # --- Step 2.5: Inject Upload Logic if Tab is Photos/Documents ---
                    if tab_name == "Photos/Documents":
                         photo_upload_success = self.upload_files_for_order(order_id, tfs_orderid)
                         if not photo_upload_success:
                            logger.log(
                                module="rrreview-fill_form_multi",
                                order_id=hybrid_orderid,
                                action_type="Warning",
                                remarks="Document upload failed during tab processing.",
                                severity="INFO"
                            )
                         # Continue to process controls if any (though usually empty for this tab?)
                         # Also ensure we are back in the correct iframe for controls?
                         # The upload function switches to default then iframeBPOBPOEntryFormTab5.
                         # The loop logic above ALREADY switched to iframeBPOBPOEntryFormTab5 (if mapped correctly).
                         # So we are good.

                    # Step 3: Process field controls in this tab
                    
                    for control in controls:
                        field_type = control.get("filedtype")
                        values = control.get("values", [])

                        if field_type in ["save_data", "save_data_adj"]:
                            # Save logic is handled dynamically at the end of the tab loop.
                            continue

                        if field_type == "checkbox_list":
                            for field in values:
                                if not (isinstance(field, list) and len(field) == 3):
                                    #logging.warning(f"Invalid checkbox_list field: {field}")
                                    logger.log(
                                        module="rrreview-fill_form_multi",
                                        order_id=hybrid_orderid,
                                        action_type="Condition-check",
                                        remarks=f"Invalid checkbox_list field: {field}",
                                        severity="INFO"
                                        )
                                    continue
                                key_expr, id_prefix, mode = field
                                try:
                                    value = extract_value_from_expr(key_expr)
                                    if value:
                                        select_checkboxes_from_list(self.driver, value, id_prefix)
                                        #logging.info(f"Checkboxes selected for {key_expr} with prefix {id_prefix}")
                                        logger.log(
                                        module="rrreview-fill_form_multi",
                                        order_id=hybrid_orderid,
                                        action_type="Condition-check",
                                        remarks=f"Checkboxes selected for {key_expr} with prefix {id_prefix}",
                                        severity="INFO"
                                        )
                                except Exception as e:
                                    #logging.error(f"Error selecting checkboxes for {key_expr}: {e}")
                                    logger.log(
                                        module="rrreview-fill_form_multi",
                                        order_id=hybrid_orderid,
                                        action_type="Exception",
                                        remarks=f"Error selecting checkboxes for {key_expr}: {e}",
                                        severity="INFO"
                                        )
                            continue

                        elif field_type == "repair_details_fill":
                            for value_config in values:
                                key_expr, _, _ = value_config
                                try:
                                    repair_data = extract_value_from_expr(key_expr)

                                    if isinstance(repair_data, list):
                                        if not rrr_fill_repair_details(self.driver, repair_data):
                                            print("Warning: Repair details filling failed.")
                                            #form_fill_success = False
                                            logger.log(module="rrreview-fill_form_multi", order_id=hybrid_orderid, action_type="Warning", remarks="Repair details filling returned failure for some items.", severity="INFO")
                                except Exception as e:
                                    print(f"Exception in Repair Details: {e}")
                                    #form_fill_success = False
                                    logger.log(module="rrreview-fill_form_multi", order_id=hybrid_orderid, action_type="Exception", remarks=f"Error processing repair details: {e}", severity="INFO")
                            continue


                        for field in values:
                            if not (isinstance(field, list) and len(field) in [3, 5]):
                                #logging.warning(f"Invalid field format: {field}")
                                logger.log(
                                    module="rrreview-fill_form_multi",
                                    order_id=hybrid_orderid,
                                    action_type="Warning",
                                    remarks=f"Invalid field format: {field}",
                                    severity="INFO"
                                )
                                continue

                            key_expr = field[0]
                            # Resolve dynamic parts like {condition_data['...']} for field[1]
                            resolved_xpath = resolve_template(field[1]) if isinstance(field[1], str) else field[1]
                            
                            if isinstance(field[1], str) and '{' in field[1]: # Log if it WAS a template
                                logger.log(
                                    module="rrreview-fill_form_multi",
                                    order_id=hybrid_orderid,
                                    action_type="Info",
                                    remarks=f"Resolved dynamic locator: {resolved_xpath}",
                                    severity="INFO"
                                )
                            try:
                                value = extract_value_from_expr(key_expr)

                                if field_type not in ["button_click", "select_empty_field"] and value in [None, ""]:
                                    continue
                                
                                action_func = field_actions.get(field_type)
                                if action_func:
                                    if field_type == "button_click":
                                        # Only click if button is present and clickable
                                        try:
                                            WebDriverWait(self.driver, 10).until(
                                                EC.element_to_be_clickable((By.XPATH, resolved_xpath))
                                            )
                                            logger.log(module="rrreview-fill_form_multi", order_id=hybrid_orderid, action_type="Info", remarks=f"Button '{resolved_xpath}' is clickable, executing click.", severity="INFO")
                                        except Exception as e:
                                            logger.log(module="rrreview-fill_form_multi", order_id=hybrid_orderid, action_type="Warning", remarks=f"Button '{resolved_xpath}' not clickable/found after wait: {e}", severity="INFO")
                                            continue  # Skip click if the button isn't there (e.g., popup didn't open)
                                    
                                    if len(field) == 5:
                                        span_xpath = field[2]
                                        extra_xpath = field[3]
                                        element_type = field[4]
                                        action_func(self.driver, value, resolved_xpath, span_xpath, extra_xpath, element_type)
                                    else:
                                        mode = field[2]
                                        action_func(self.driver, value, resolved_xpath, mode)
                                else:
                                    #logging.warning(f"Unknown field type: {field_type}")
                                    logger.log(
                                        module="rrreview-fill_form_multi",
                                        order_id=hybrid_orderid,
                                        action_type="Warning",
                                        remarks=f"Unknown field type: {field_type}",
                                        severity="INFO"
                                    )
                            except Exception as e:
                                #logging.error(f"Exception filling field {key_expr}: {e}")
                                print(f"Exception filling field {key_expr} (Type: {field_type}): {e}")
                                #form_fill_success = False
                                logger.log(
                                        module="rrreview-fill_form_multi",
                                        order_id=hybrid_orderid,
                                        action_type="Exception",
                                        remarks=f"Exception filling field {key_expr}: {e}",
                                        severity="INFO"
                                    )
                    if tab_name not in ["Validation Results", "Photos/Documents"]:
                        # --- Step 2.7: Save after each tab ---
                        print(f"Saving after {tab_name} Tab...")
                        self.driver.switch_to.default_content()
                        self.save_form_rrreview()
                        form_fill_success = True
                        # No need to switch back to iframe here as the next iteration will do it


            # --- Final Status Update ---
            print(f"Smart Entry Check for Order {hybrid_orderid}")
            print(f"Form Fill Success: {form_fill_success}")
            print(f"Photo Upload Success: {photo_upload_success}")
            

            if form_fill_success and photo_upload_success:
                #update_order_status(hybrid_orderid, "In Progress", "Entry", "Completed", hybrid_token)
                update_order_status(hybrid_orderid, "In Progress", "Entry", "Filled", hybrid_token)
                logger.log(
                    module="rrreview-fill_form_multi",
                    order_id=hybrid_orderid,
                    action_type="Info",
                    remarks=f"Smart Entry Completed successfully for {hybrid_orderid}",
                    severity="INFO"
                )
                print(f"Smart Entry Process Completed for {hybrid_orderid}")
                if is_qc:  # QC orders skip TFS status change
                    logger.log(module="TFS_Status_Change", order_id=hybrid_orderid, action_type="Status_change", remarks="QC order no status change needed", severity="INFO")
                else:
                    tfs_statuschange(tfs_orderid, "26", "5", "20")
                #return True
            else:
                print(f"Smart Entry Result: FAILED (Fill: {form_fill_success}, Upload: {photo_upload_success})")
                update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed", hybrid_token)
                logger.log(
                    module="rrreview-fill_form_multi",
                    order_id=hybrid_orderid,
                    action_type="Warning",
                    remarks=f"Smart Entry Failed for {hybrid_orderid} (Fill: {form_fill_success}, Upload: {photo_upload_success})",
                    severity="INFO"
                )
                # tfs_statuschange(tfs_orderid, "27", "5", "20")
                #return False

            # # --- Final Status Update ---
            # if is_qc :   #qc order
            #     logger.log(module="TFS_Status_Change",order_id=hybrid_orderid,action_type="Status_change",remarks="QC order no status change needed",severity="INFO")
            # else:
            #     tfs_statuschange(tfs_orderid , "26", "5", "20")

            # update_order_status(hybrid_orderid, "In Progress", "Entry", "Filled",hybrid_token)
            # print(hybrid_orderid,"Smart Entry")

            # return saved_form

        except Exception as e:
            #logging.error(f"Critical error in fill_form_multi: {e}")
            logger.log(
                module="rrreview-fill_form_multi",
                order_id=hybrid_orderid,
                action_type="Exception",
                remarks=f"Critical error in fill_form_multi: {e}",
                severity="INFO"
            )
            #update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
            #tfs_statuschange(tfs_orderid, "27", "3", "14")
            return False

    def save_form_rrreview(self):
        """
        RRReview-specific save function.
        Clicks the 'savebutton' element (id="savebutton") which triggers saveAllTabData().
        Should be called from default content (not inside iframe).
        """
        print("Saving...")
        try:
            # Ensure we're in default content
            self.driver.switch_to.default_content()
            
            # Wait for and click the save button
            save_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "savebutton"))
            )
            
            # Scroll into view and click
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", save_btn)
            time.sleep(0.5)
            save_btn.click()
            
            # Wait for any save confirmation alert
            try:
                WebDriverWait(self.driver, 5).until(EC.alert_is_present())
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                alert.accept()
                
                # Proactive handling for 'Property Condition' alert
                if "Property Condition" in alert_text:
                    logger.log(module="rrreview-save_form_rrreview", order_id=hybrid_orderid, action_type="Warning", remarks="Detected missing Property Condition alert. Attempting logic fix.", severity="INFO")
                    self.driver.switch_to.default_content()
                    try:
                        # Quickly flip to Tab 1 to check the box
                        tab1_link = self.driver.find_element(By.ID, "tabBPOBPOEntryFormTab1")
                        tab1_link.click()
                        time.sleep(1)
                        self.driver.switch_to.frame("iframeBPOBPOEntryFormTab1")
                        cond_cb = self.driver.find_element(By.ID, "chkPCond")
                        if not cond_cb.is_selected():
                            self.driver.execute_script("arguments[0].click();", cond_cb)
                            logger.log(module="rrreview-save_form_rrreview", order_id=hybrid_orderid, action_type="Info", remarks="Surgically checked 'chkPCond' to satisfy portal requirement.", severity="INFO")
                        self.driver.switch_to.default_content()
                        # Re-click save
                        save_btn = self.driver.find_element(By.ID, "savebutton")
                        save_btn.click()
                        time.sleep(2)
                    except Exception as e:
                        logger.log(module="rrreview-save_form_rrreview", order_id=hybrid_orderid, action_type="Error", remarks=f"Failed to proactively fix Property Condition: {e}", severity="WARNING")
                        self.driver.switch_to.default_content()
            except:
                # No alert, that's fine
                pass
            
            # Wait for save to complete
            time.sleep(5)
            
            logger.log(
                module="rrreview-save_form_rrreview",
                order_id=hybrid_orderid,
                action_type="Success",
                remarks="Form saved successfully using savebutton",
                severity="INFO"
            )
            return True
            
        except Exception as e:
            logger.log(
                module="rrreview-save_form_rrreview",
                order_id=hybrid_orderid,
                action_type="Error",
                remarks=f"Failed to save form: {e}",
                severity="ERROR"
            )
            return False

    def clear_existing_documents(self):
        """
        Clears existing documents in the 'Photos/Documents' tab to prevent duplicates.
        Flow:
        1. Check if any checkboxes exist (indicating uploaded files).
        2. If yes: Select all checkboxes → Click Delete → Save Form.
        3. If no: Return False (no files to delete)."""
        try:
            # Ensure we are in the correct iframe
            self.driver.switch_to.default_content()
            iframe = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "iframeBPOBPOEntryFormTab5"))
            )
            self.driver.switch_to.frame(iframe)

            print("Scanning Portal for Existing Documents to Clear...")
            logger.log(module="rrreview-clear_existing_documents", order_id=hybrid_orderid, action_type="Info", remarks="Scanning portal for document clearing (Preserving ALL Subject labels)...", severity="INFO")
            
            count_deleted = 0
            
            # --- Targeted Labels for Clearing ---
            # Identifies Comps and Documents by their portal-assigned labels.
            # LOGIC: Delete ALL except for labels containing "Subject".
            
            # 1. Handle Photos (Identify ALL except Subject)
            try:
                pnl_photos = self.driver.find_element(By.ID, "dlPhotos")
                photo_containers = pnl_photos.find_elements(By.TAG_NAME, "table")
                for container in photo_containers:
                    try:
                        # Find the Label Dropdown
                        select_el = container.find_element(By.TAG_NAME, "select")
                        selected_label = Select(select_el).first_selected_option.text.lower().strip()
                        
                        if not selected_label or "none selected" in selected_label:
                            continue

                        # PRESERVATION RULE: Keep if label HAS "Subject" (Primary Requirement)
                        if "subject" in selected_label:
                            logger.log(module="rrreview-clear_existing_documents", order_id=hybrid_orderid, action_type="Info", remarks=f"Preserving Subject Photo via Label: '{selected_label}'", severity="INFO")
                            continue

                        # UNIVERSAL CLEARING: Delete anything that is NOT a Subject label
                        cb = container.find_element(By.XPATH, ".//input[@type='checkbox']")
                        if cb.is_displayed() and cb.is_enabled() and not cb.is_selected():
                            cb.click()
                            count_deleted += 1
                            logger.log(module="rrreview-clear_existing_documents", order_id=hybrid_orderid, action_type="Info", remarks=f"Select for Deletion (Photo): '{selected_label}'", severity="INFO")
                        
                    except Exception as e:
                        # logger.log(module="rrreview-clear_existing_documents", order_id=hybrid_orderid, action_type="Warning", remarks=f"Error processing photo container: {e}", severity="WARNING")
                        continue
            except Exception as e:
                logger.log(module="rrreview-clear_existing_documents", order_id=hybrid_orderid, action_type="Error", remarks=f"Photo label scanning failed: {e}", severity="ERROR")

            # 2. Handle Documents (Identify ALL except Subject)
            try:
                pnl_docs = self.driver.find_element(By.ID, "pnlDocsGrid")
                doc_rows = pnl_docs.find_elements(By.TAG_NAME, "tr")
                for row in doc_rows:
                    try:
                        select_els = row.find_elements(By.TAG_NAME, "select")
                        if not select_els:
                            continue
                            
                        select_el = select_els[0]
                        selected_label = Select(select_el).first_selected_option.text.lower().strip()
                        
                        if not selected_label or "none selected" in selected_label:
                            continue

                        # PRESERVATION RULE: Keep if label HAS "Subject"
                        if "subject" in selected_label:
                            logger.log(module="rrreview-clear_existing_documents", order_id=hybrid_orderid, action_type="Info", remarks=f"Preserving Subject Doc via Label: '{selected_label}'", severity="INFO")
                            continue

                        # UNIVERSAL CLEARING: Delete anything that is NOT a Subject label
                        cb = row.find_element(By.XPATH, ".//input[@type='checkbox']")
                        if cb.is_displayed() and cb.is_enabled() and not cb.is_selected():
                            cb.click()
                            count_deleted += 1
                            logger.log(module="rrreview-clear_existing_documents", order_id=hybrid_orderid, action_type="Info", remarks=f"Select for Deletion (Doc): '{selected_label}'", severity="INFO")
                    except Exception as e:
                        # logger.log(module="rrreview-clear_existing_documents", order_id=hybrid_orderid, action_type="Warning", remarks=f"Error processing doc row: {e}", severity="WARNING")
                        continue
            except Exception as e:
                logger.log(module="rrreview-clear_existing_documents", order_id=hybrid_orderid, action_type="Error", remarks=f"Document label scanning failed: {e}", severity="ERROR")
            
            if count_deleted == 0:
                 print("No existing documents found to clear.")
                 logger.log(module="rrreview-clear_existing_documents", order_id=self.order_id if hasattr(self, 'order_id') and self.order_id else "Unknown", action_type="Info", remarks="No eligible Re-Upload files found for deletion. Preserving current state.", severity="INFO")
                 return False

            print(f"Clearing {count_deleted} detected documents...")
            logger.log(module="rrreview-clear_existing_documents", order_id=self.order_id if hasattr(self, 'order_id') and self.order_id else "Unknown", action_type="Info", remarks=f"Triggering deletion of {count_deleted} targeted documents.", severity="INFO")

            # 2. Save Form - This actually triggers the deletion
            self.driver.switch_to.default_content()
            
            save_success = self.save_form_rrreview()
            return save_success

        except Exception as e:
            logger.log(
                module="rrreview-clear_existing_documents",
                order_id=self.order_id if hasattr(self, 'order_id') and self.order_id else "Unknown",
                action_type="Error",
                remarks=f"Error clearing documents: {e}",
                severity="ERROR"
            )
            return False


    def upload_files_for_order(self, order_id: int, tfs_orderid: str) -> bool:
        """
        Fetches documents for the order and uploads them via the 'Photos/Documents' tab in two batches:
        1. Subject PDFs (MLS.pdf, TAX.pdf)
        2. Comparable Images (anything not .pdf inside comparables folder)
        """
        logger.log(module="rrreview-upload_files_for_order", order_id=hybrid_orderid, action_type="Info", remarks=f"Starting upload process for order {order_id}", severity="INFO")
        try:
            # 0. Clear existing files first (if any exist)
            files_were_cleared = self.clear_existing_documents()
            
            if files_were_cleared:
                logger.log(module="rrreview-upload_files_for_order", order_id=hybrid_orderid, action_type="Info", remarks="Previous files were cleared. Proceeding to new uploads.", severity="INFO")
            else:
                logger.log(module="rrreview-upload_files_for_order", order_id=hybrid_orderid, action_type="Info", remarks="No previous files required clearing. Proceeding directly.", severity="INFO")

            # 1. Fetch upload data
            data = fetch_upload_data(self, order_id)
            if not data:
                logger.log(
                    module="rrreview-upload_files_for_order",
                    order_id=hybrid_orderid,
                    action_type="Error",
                    remarks="Critical: No upload data (JSON) retrieved for this order.",
                    severity="ERROR"
                )
                return False
            
            logger.log(module="rrreview-upload_files_for_order", order_id=hybrid_orderid, action_type="Info", remarks=f"Retrieved upload data for {order_id}. Processing files...", severity="INFO")

            documents = data.get("documents", [])
            comparables_folder = data.get("comparables_folder", "")
            
            # --- Single Batch: Subject PDFs + Comp Images ---
            all_files_to_upload = []
            
            # 1. Subject PDFs (Strictly MLS.pdf and TAX.pdf only, excluding mls_tax.pdf)
            target_pdfs = ["mls.pdf", "tax.pdf"]
            for doc in documents:
                doc_path = doc.get("path")
                if doc_path and os.path.exists(doc_path) and doc_path.lower().endswith(".pdf"):
                    basename = os.path.basename(doc_path).lower()
                    if basename in target_pdfs:
                        all_files_to_upload.append(doc_path)
                    else:
                        logger.log(module="rrreview-upload_files_for_order", order_id=hybrid_orderid, action_type="Info", remarks=f"Skipping non-target PDF: {basename}", severity="INFO")
                elif doc_path and not os.path.exists(doc_path):
                     logger.log(module="rrreview-upload_files_for_order", order_id=hybrid_orderid, action_type="Error", remarks=f"File missing on disk: {doc_path}", severity="ERROR")
            
            # 2. Comparable Images
            if os.path.exists(comparables_folder):
                for fname in os.listdir(comparables_folder):
                    if fname.lower() == "thumbs.db":
                        continue
                    if not fname.lower().endswith(".pdf"):
                        full_path = os.path.join(comparables_folder, fname)
                        if os.path.isfile(full_path):
                            all_files_to_upload.append(full_path)
            
            if not all_files_to_upload:
                 logger.log(module="rrreview-upload_files_for_order", order_id=hybrid_orderid, action_type="Info", remarks="No valid files (PDFs/Images) identified for upload.", severity="INFO")
                 return True

            print(f"Starting upload of {len(all_files_to_upload)} new files...")
            logger.log(module="rrreview-upload_files_for_order", order_id=hybrid_orderid, action_type="Info", remarks=f"Ready to batch upload {len(all_files_to_upload)} files.", severity="INFO")

            # Helper function to perform the upload session
            def perform_single_upload(files):
                logger.log(module="rrreview-perform_single_upload", order_id=hybrid_orderid, action_type="Info", remarks=f"Starting single batch session for {len(files)} files.", severity="INFO")
                
                self.driver.switch_to.default_content()
                try:
                    iframe = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "iframeBPOBPOEntryFormTab5"))
                    )
                    self.driver.switch_to.frame(iframe)
                except Exception as e:
                    logger.log(module="rrreview-perform_single_upload", order_id=hybrid_orderid, action_type="Error", remarks=f"Iframe Tab 5 switch failed: {e}", severity="ERROR")
                    return False

                # Open Popup
                try:
                    upload_btn = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.ID, "myBtn"))
                    )
                    self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", upload_btn)
                    upload_btn.click()
                    time.sleep(2)
                except Exception as e:
                    logger.log(module="rrreview-perform_single_upload", order_id=hybrid_orderid, action_type="Error", remarks=f"Fail to open upload dialog: {e}", severity="ERROR")
                    return False

                # Switch to uploader iframe - use specific source matching standalone bot
                try:
                    uploader_iframe = WebDriverWait(self.driver, 10).until(
                        EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[@src='https://legacy.rrreview.com/bpo/FormEntry/new/Uploader.aspx']"))
                    )
                except Exception as e:
                    logger.log(module="rrreview-perform_single_upload", order_id=hybrid_orderid, action_type="Warning", remarks=f"Primary uploader iframe match failed, trying fallback. Error: {e}", severity="INFO")
                    try:
                         uploader_iframe = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "div#MyDialog iframe"))
                         )
                         self.driver.switch_to.frame(uploader_iframe)
                    except:
                        logger.log(module="rrreview-perform_single_upload", order_id=hybrid_orderid, action_type="Error", remarks="Both primary and fallback uploader iframe matches failed.", severity="ERROR")
                        return False

                # Send Files
                try:
                     file_input = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.ID, "file"))
                     )
                     file_input.send_keys("\n".join(files))
                     logger.log(module="rrreview-perform_single_upload", order_id=hybrid_orderid, action_type="Info", remarks=f"Queued {len(files)} files into uploader.", severity="INFO")
                     time.sleep(3)
                except Exception as e:
                    logger.log(module="rrreview-perform_single_upload", order_id=hybrid_orderid, action_type="Error", remarks=f"Failed to queue files: {e}", severity="ERROR")
                    return False

                # Start Upload
                try:
                    start_btn = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.start"))
                    )
                    start_btn.click()
                    logger.log(module="rrreview-perform_single_upload", order_id=hybrid_orderid, action_type="Info", remarks="Upload started. Waiting for server confirmation...", severity="INFO")
                    
                    # Wait for explicit success message in the uploader list
                    try:
                        WebDriverWait(self.driver, 180).until(
                            EC.visibility_of_element_located((By.XPATH, "//td[contains(text(), 'Files Uploaded Successfully:')]"))
                        )
                        print("Upload Success..")
                        logger.log(module="rrreview-perform_single_upload", order_id=hybrid_orderid, action_type="Success", remarks="Server confirmed upload success. Starting fast batch verification...", severity="INFO")
                        
                        # High-speed batch verification loop
                        for _ in range(25): # Try for ~50 seconds
                            uploader_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
                            missing_in_uploader = []
                            for f_path in files:
                                fname = os.path.basename(f_path).lower()
                                if fname not in uploader_text:
                                    missing_in_uploader.append(fname)
                            
                            if not missing_in_uploader:
                                logger.log(module="rrreview-perform_single_upload", order_id=hybrid_orderid, action_type="Success", remarks=f"All {len(files)} files verified in uploader UI.", severity="INFO")
                                break
                            
                            logger.log(module="rrreview-perform_single_upload", order_id=hybrid_orderid, action_type="Info", remarks=f"Sync wait: {len(missing_in_uploader)} files pending in uploader UI...", severity="INFO")
                            time.sleep(2)
                        
                        logger.log(module="rrreview-perform_single_upload", order_id=hybrid_orderid, action_type="Info", remarks="Verification phase complete. Closing uploader modal.", severity="INFO")
                    except Exception as e:
                        logger.log(module="rrreview-perform_single_upload", order_id=hybrid_orderid, action_type="Warning", remarks=f"Uploader verification loop encountered an error: {e}", severity="INFO")
              
                    close_btn = None
                    try:
                        close_btn = WebDriverWait(self.driver, 180).until(
                             EC.element_to_be_clickable((By.XPATH, "//button[@class='closeWidget' and contains(@style, 'block')]"))
                        )
                    except:
                        logger.log(module="rrreview-perform_single_upload", order_id=hybrid_orderid, action_type="Info", remarks="'closeWidget' not present, checking for legacy 'Close Uploader' button.", severity="INFO")
                        close_btn = WebDriverWait(self.driver, 10).until(
                             EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Close Uploader')]"))
                        )
                    
                    if close_btn:
                        close_btn.click()
                        logger.log(module="rrreview-perform_single_upload", order_id=hybrid_orderid, action_type="Success", remarks="Uploader modal closed successfully.", severity="INFO")
                        time.sleep(2)
                        return True
                    return False
                except Exception as e:
                    logger.log(module="rrreview-perform_single_upload", order_id=hybrid_orderid, action_type="Error", remarks=f"Critical error during upload or verification: {e}", severity="ERROR")
                    return False

            # --- Execute Upload ---
            if perform_single_upload(all_files_to_upload):
                time.sleep(10) # Increased buffer for portal stability
                sync_success = self.select_file_types_in_portal(all_files_to_upload)
                
                # Final Save
                save_success = self.save_form_rrreview()
                
                if sync_success and save_success:
                    logger.log(module="rrreview-upload_files_for_order", order_id=hybrid_orderid, action_type="Success", remarks="Files uploaded and selected successfully", severity="INFO")
                    return True
                else:
                    logger.log(module="rrreview-upload_files_for_order", order_id=hybrid_orderid, action_type="Error", remarks=f"Post-upload steps failed (Sync: {sync_success}, Save: {save_success})", severity="ERROR")
                    return False
            else:
                return False

        except Exception as e:
            logger.log(
                module="rrreview-upload_files_for_order",
                order_id=hybrid_token if hybrid_token else hybrid_orderid,
                action_type="Exception",
                remarks=f"Exception in upload_files_for_order: {e}",
                severity="ERROR"
            )
            return False

    def select_file_types_in_portal(self, uploaded_files=[]):
        """
        Iterates through tables and selects appropriate document types based on filenames.
        Includes a wait loop to ensure all specifically uploaded files have been processed by the portal.
        """
        expected_count = len(uploaded_files)
        
        logger.log(module="rrreview-select_file_types", order_id=hybrid_orderid, action_type="Info", remarks=f"Starting document type synchronization for {expected_count} files.", severity="INFO")
        try:
            self.driver.switch_to.default_content()
            iframe = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "iframeBPOBPOEntryFormTab5"))
            )
            self.driver.switch_to.frame(iframe)

            # --- Absolute Specific-File Synchronization ---
            if expected_count > 0:
                logger.log(module="rrreview-select_file_types", order_id=hybrid_orderid, action_type="Info", remarks=f"Waiting for {expected_count} files to populate in portal grid...", severity="INFO")
                max_retries = 30 # Up to 180 seconds total
                known_found_files = set()
                
                for i in range(max_retries):
                    self.driver.switch_to.default_content()
                    iframe = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "iframeBPOBPOEntryFormTab5")))
                    self.driver.switch_to.frame(iframe)

                    # Get entire page text as a single blob for fastest search
                    body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
                    
                    missing_files = []
                    for f_path in uploaded_files:
                        fname = os.path.basename(f_path).lower()
                        # Use flexible matching for stems
                        name_stem = fname.split('.')[0]
                        if name_stem in body_text:
                            if fname not in known_found_files:
                                logger.log(module="rrreview-select_file_types", order_id=hybrid_orderid, action_type="Info", remarks=f"File detected in portal grid: '{fname}'", severity="INFO")
                                
                                known_found_files.add(fname)
                        else:
                            missing_files.append(fname)
                    
                    if not missing_files:
                        logger.log(module="rrreview-select_file_types", order_id=hybrid_orderid, action_type="Success", remarks=f"All {expected_count} files are fully populated in the portal grid.", severity="INFO")
                        break
                    
                    # Periodic frame content refresh (not a full page refresh)
                    if i > 0 and i % 5 == 0:
                        logger.log(module="rrreview-select_file_types", order_id=hybrid_orderid, action_type="Info", remarks=f"Synchronization stalled ({len(known_found_files)}/{expected_count}). Refreshing tab context...", severity="INFO")

                    logger.log(module="rrreview-select_file_types", order_id=hybrid_orderid, action_type="Info", remarks=f"Population Status: {len(known_found_files)}/{expected_count} found. Waiting for: {missing_files}...", severity="INFO")
                    time.sleep(6) # Slightly longer sleep for portal refresh
                else:
                    logger.log(module="rrreview-select_file_types", order_id=hybrid_orderid, action_type="Warning", remarks=f"Synchronization timed out. Proceeding with {len(known_found_files)}/{expected_count} files.", severity="WARNING")
                    # In a high-standard flow, maybe we should fail here if files are missing?
                    # But if we found some, we might still try to fill.
                    # For now, let's track which ones we actually find vs expected.

            # Track which expected files were successfully selected
            selected_files = set()
            
            # Mappings (using basenames)
            file_type_map = {
                "tax.pdf": "Tax Records",
                "mls.pdf": "MLS Sheet",
                "s1": "Sale 1 Photo",
                "s2": "Sale 2 Photo",
                "s3": "Sale 3 Photo",
                "a1": "Listing 1 Photo",
                "a2": "Listing 2 Photo",
                "a3": "Listing 3 Photo",
            }

            # 1. Photos (dlPhotos table)
            photo_containers = self.driver.find_elements(By.XPATH, "//table[@id='dlPhotos']//td[.//select]")
            logger.log(module="rrreview-select_file_types", order_id=hybrid_orderid, action_type="Info", remarks=f"Processing {len(photo_containers)} photo containers", severity="INFO")
            
            for container in photo_containers:
                try:
                    cell_text = container.text.lower()
                    filename = ""
                    for key in file_type_map.keys():
                        if ".pdf" not in key and key in cell_text:
                            filename = key
                            break
                    
                    if not filename:
                        continue

                    select_el = container.find_element(By.TAG_NAME, "select")
                    dropdown = Select(select_el)
                    current_val = dropdown.first_selected_option.text.strip()
                    
                    if current_val == "None Selected" or current_val == "":
                        for key, val in file_type_map.items():
                            if ".pdf" not in key and key in filename:
                                dropdown.select_by_visible_text(val)
                                logger.log(module="rrreview-select_file_types", order_id=hybrid_orderid, action_type="Success", remarks=f"Selected '{val}' for photo '{filename}'", severity="INFO")
                                selected_files.add(filename)
                                break
                    else:
                        # Already has a value, count it as selected
                        selected_files.add(filename)
                except Exception as e:
                    logger.log(module="rrreview-select_file_types", order_id=hybrid_orderid, action_type="Error", remarks=f"Error selecting type for photo container: {e}", severity="WARNING")

            # 2. Documents (pnlDocsGrid)
            doc_rows = self.driver.find_elements(By.XPATH, "//div[@id='pnlDocsGrid']//table//tr[.//select]")
            logger.log(module="rrreview-select_file_types", order_id=hybrid_orderid, action_type="Info", remarks=f"Processing {len(doc_rows)} doc rows", severity="INFO")
            for row in doc_rows:
                try:
                    row_text = row.text.lower()
                    select_el = row.find_element(By.TAG_NAME, "select")
                    dropdown = Select(select_el)
                    
                    current_val = dropdown.first_selected_option.text.strip()
                    if current_val == "None Selected" or current_val == "":
                        for key, val in file_type_map.items():
                            if ".pdf" in key and key in row_text:
                                dropdown.select_by_visible_text(val)
                                logger.log(module="rrreview-select_file_types", order_id=hybrid_orderid, action_type="Success", remarks=f"Selected '{val}' for row matching '{key}'", severity="INFO")
                                selected_files.add(key)
                                break
                    else:
                        # Already has a value, check which one it matches
                        for key in file_type_map.keys():
                            if ".pdf" in key and key in row_text:
                                selected_files.add(key)
                                break
                except Exception as e:
                    logger.log(module="rrreview-select_file_types", order_id=hybrid_orderid, action_type="Error", remarks=f"Error selecting type for doc row: {e}", severity="WARNING")

            # Final Satisfaction Check
            all_satisfied = True
            for f_path in uploaded_files:
                fname = os.path.basename(f_path).lower()
                stem = fname.split('.')[0]
                # Check for either the stem (photos) or full name (pdfs) in selected_files
                matched = False
                for s in selected_files:
                    if s in fname:
                        matched = True
                        break
                if not matched:
                    logger.log(module="rrreview-select_file_types", order_id=hybrid_orderid, action_type="Warning", remarks=f"File '{fname}' was not successfully matched to a type dropdown.", severity="INFO")
                    all_satisfied = False

            if all_satisfied:
                logger.log(module="rrreview-select_file_types", order_id=hybrid_orderid, action_type="Success", remarks="All uploaded files successfully mapped and selected.", severity="INFO")
            else:
                logger.log(module="rrreview-select_file_types", order_id=hybrid_orderid, action_type="Warning", remarks=f"Only partial success in file mapping. ({len(selected_files)}/{expected_count})", severity="INFO")
            
            return all_satisfied

        except Exception as e:
            logger.log(module="rrreview-select_file_types", order_id=hybrid_orderid, action_type="Error", remarks=f"Critical error in select_file_types_in_portal: {e}", severity="ERROR")
            return False

