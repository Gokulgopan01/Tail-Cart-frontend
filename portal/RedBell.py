
import os
import re
import time
import logging
from tkinter import messagebox
import requests
import json
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from dotenv import load_dotenv

from condtions.all_portal_conditions import generate_condition_data

from integrations.hybrid_bpo_api import HybridBPOApi
from utils.glogger import GLogger
from utils.helper import (clean_address, data_filling_text, extract_data_sections, fetch_upload_data, fill_repair_details, get_nested, get_order_address_from_assigned_order, 
handle_login_status, javascript_excecuter_filling, load_form_config_and_data, params_check, radio_btn_click, resource_path, save_form, save_form_adj,select_checkboxes_from_list,
select_field, setup_driver, single_checkbox, update_client_account_status, update_order_status, update_portal_login_confirmation_status, tfs_statuschange)

from config import env
logger = GLogger()

# Load variables from .env file
load_dotenv()

# Retrieve API URLs from environment variables
ASSIGNEDORDERS_URL = os.getenv("ASSIGNEDORDERS_URL")  
                   
process_type, hybrid_orderid, hybrid_token = params_check()

logger.log(
    module="Redbell-global",
    order_id=hybrid_orderid,
    action_type="Info",
    remarks=f"type,orderid,token,{process_type},{hybrid_orderid},{hybrid_token}",
    severity="INFO"
)

class RedBell:
    def __init__(self, username, password, portal_url, portal_name, proxy, session,account_id, portal_key):
        self.username = username
        self.password = password
        self.portal_url = portal_url
        self.portal_name = portal_name
        self.proxy = proxy
        self.session = session
        self.driver = None
        self.order_details = None
        self.order_id = None
        self.account_id=account_id
        self.portal_key = portal_key


    def login_to_portal(self):
        try:
            setup_driver(self)
            api_url = env.AUTHENTICATOR_API_URL
            headers = {'Content-Type': env.API_HEADERS_CONTENT_TYPE}
            payload = json.dumps({"username": self.username})

            response = requests.post(api_url, headers=headers, data=payload)
            response.raise_for_status()
            api_response = response.json()

            if api_response.get("status") == "success":
                redbell_cookie = api_response["cookies"].get(".ASPXAUTH")
                if redbell_cookie:
                    self.driver.get(self.portal_url)
                    self.driver.add_cookie({'name': '.ASPXAUTH', 'value': redbell_cookie})
                    self.driver.get(f"{self.portal_url}/Index")

                    title = self.driver.current_url
                    login_check_keyword = ["VendorPortal/Index", "DailyUpdates"]
                    #handle_login_status(title, self.username, login_check_keyword, self.portal_name)

                    # Setup session using cookie
                    session = requests.Session()
                    session.cookies.set('.ASPXAUTH', redbell_cookie, domain="valuationops.homegenius.com")
                    self.session = session

                    #process_type = "SmartEntry"  # Manually set for testing
                    #process_type="PortalLogin"
                    #process_type="AutoLogin"
                    if process_type == "SmartEntry":
                        orders, session = self.fetch_data(self.session)
                        self.redbell_formopen(
                            orders=orders,
                            session=session,
                            merged_json=None,
                            order_details=self.order_details,
                            order_id=self.order_id
                        )
                        #input()
                        #print("Filled")
                        # redbell_formopen_fill(self, orders, session,  merged_json=None,
                        #     order_details=self.order_details,
                        #     order_id=self.order_id)
                    # elif process_type =="PortalLogin":
                    #      handle_login_status(title, self.username, login_check_keyword, self.portal_name)   
                    else:  
                        update_portal_login_confirmation_status(hybrid_orderid)  
                        handle_login_status(title, self.username, login_check_keyword, self.portal_name,self.driver)
                        #update_portal_login_confirmation_status(hybrid_orderid)

                        logger.log(
                            module="Redbell-login_to_portal",
                            order_id=hybrid_orderid,
                            action_type="Info",
                            remarks="After the handle_login_status call",
                            severity="INFO"
                        )
                    return self.driver, self.session

                else:

                    logger.log(
                    module="Redbell-login_to_portal",
                    order_id=hybrid_orderid,
                    action_type="Exception",
                    remarks=f"Cookie '.ASPXAUTH' not found in API response.",
                    severity="INFO"
                )
            else:

                logger.log(
                    module="Redbell-login_to_portal",
                    order_id=hybrid_orderid,
                    action_type="Exception",
                    remarks=f"API call failed: {api_response.get('status')}",
                    severity="INFO"
                )

        except requests.exceptions.RequestException as e:

            logger.log(
            module="Redbell-login_to_portal",
            order_id=hybrid_orderid,
            action_type="Exception",
            remarks=f"API request failed: {e}",
            severity="INFO"
        )
        except json.JSONDecodeError as e:

            logger.log(
            module="Redbell-login_to_portal",
            order_id=hybrid_orderid,
            action_type="Exception",
            remarks=f"Failed to decode JSON response: {e}",
            severity="INFO"
        )
        except Exception as e:

            logger.log(
            module="Redbell-login_to_portal",
            order_id=hybrid_orderid,
            action_type="Exception",
            remarks=f"An error occurred: {e}",
            severity="INFO"
        )

        title = "MFA FAILED"
        login_check_keyword = ["False"]
        if process_type == "SmartEntry":
            update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
        update_client_account_status(self.account_id)
        handle_login_status(title, self.username, login_check_keyword, self.portal_name,self.driver)
        return None, None

    def fetch_data(self, session):
        try:
            url = "https://valuationops.homegenius.com/VendorPortal/InprogressOrder"
            response = session.get(url)
            if response.status_code != 200:

                logger.log(
                    module="Redbell-fetch_data",
                    order_id=hybrid_orderid,
                    action_type="Condition_check",
                    remarks=f"Error fetching orders: Invalid response from server",
                    severity="INFO"
                )
                return [], session

            cookies = session.cookies.get_dict()
            headers = self.get_headers({
                'accept': '*/*',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'origin': 'https://valuationops.homegenius.com',
                'referer': url,
                'x-requested-with': 'XMLHttpRequest',
            })
            data = {
                '__aweconid': 'Grid',
                'pageSize': '1000',
                'page': '1',
                'tzo': '-330',
            }
            order_response = requests.post(
                'https://valuationops.homegenius.com/VendorPortal/GetMyOrderItem',
                cookies=cookies,
                headers=headers,
                data=data,
            )
            if order_response.status_code == 200:
                orders = order_response.json().get('dt', {}).get('it', [])
                return orders, session
            else:

                logger.log(
                    module="Redbell-fetch_data",
                    order_id=hybrid_orderid,
                    action_type="Condition_check",
                    remarks=f"Failed to fetch orders. Server returned error.",
                    severity="INFO"
                )
                return [], session
        except Exception as e:

            logger.log(
                    module="Redbell-fetch_data",
                    order_id=hybrid_orderid,
                    action_type="Exception",
                    remarks=f"Error fetching data: {e}",
                    severity="INFO"
                )
            return [], session

    def get_headers(self, additional_headers={}):
        headers = {
            'authority': 'valuationops.homegenius.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'en-US,en;q=0.5',
            'referer': 'https://valuationops.homegenius.com/VendorPortal',
            'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Brave";v="110"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        }
        headers.update(additional_headers)
        return headers

    def redbell_formopen(self, orders, session, merged_json, order_details, order_id):
        # hybrid_orderid=163
        # hybrid_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyaWQiOjI2LCJlbWFpbCI6Im5hbmRodV9rcmlzaG5hQGVjZXNpc2dyb3Vwcy5jb20iLCJyb2xlIjoyLCJpYXQiOjE3NTI3NDg2NjgsImV4cCI6MTc1MzYxMjY2OH0.Itsc57tAJ08YEyCS-HaBYJqn-lpceWz3O3cGXezgHH8"
        orders_from_api = HybridBPOApi.get_entry_order(hybrid_orderid) 
        if not orders_from_api:  # Check if the order list is empty
            #print("No orders found.")
            logger.log(
                    module="Redbell-redbell_formopen",
                    order_id=hybrid_orderid,
                    action_type="Condition_check",
                    remarks=f"No orders found.",
                    severity="INFO"
                )
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
            order_details_from_api,tfs_orderid,is_qc, master_order_id =get_order_address_from_assigned_order(order_id,hybrid_token)
            print("order_details_from_api:", order_details_from_api)
            logger.log(
                    module="Redbell-redbell_formopen",
                    order_id=hybrid_orderid,
                    action_type="Condition_check",
                    remarks=f"order_details_from_api: {order_details_from_api}",
                    severity="INFO"
                )

        # if not orders:

        logger.log(
                module="Redbell-redbell_formopen",
                order_id=hybrid_orderid,
                action_type="Condition_check",
                remarks=f"Starting form open process",
                severity="INFO"
            )
        target_genorderid =order_details_from_api
        form_types = ["Interior Enhanced BPO",'Interior BPO - W Rentals','Exterior Enhanced BPO','Interior BPO','Exterior BPO','Exterior BPO - W Rentals','5 Day MIT ARBPO','5 Day Interior Appraiser Reconciled BPO','5 Day Exterior Appraiser Reconciled BPO','5 Day Exterior BPO - W Rentals','5 Day Exterior BPO','5 Day Interior BPO','5 Day Interior BPO - W Rentals',"3 Day Exterior BPO - W Rentals","Interior BPO"]
        if not orders:

            logger.log(
                    module="Redbell-redbell_formopen",
                    order_id=hybrid_orderid,
                    action_type="Condition_check",
                    remarks=f"No orders in portal",
                    severity="INFO"
                )
            update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
            return

        matched, order, status = self.find_matching_order(orders, target_genorderid, form_types, order_id,tfs_orderid)

        if matched and status == "matched":
            order_url = f"https://valuationops.homegenius.com/VendorPortal/EditReport?ItemId={order['ItemId']}&EntityType=Vendor"

            logger.log(
                    module="Redbell-redbell_formopen",
                    order_id=hybrid_orderid,
                    action_type="Condition_check",
                    remarks=f"Form matched. Opening in browser.",
                    severity="INFO"
                )
            
            self.redbell_launch_browser_and_open_form(order_url, session)
            redbell_formopen_fill(self, order, session, merged_json, order_details, order_id,tfs_orderid,is_qc)
           
        elif not matched:

            logger.log(
                    module="Redbell-redbell_formopen",
                    order_id=hybrid_orderid,
                    action_type="Condition_check",
                    remarks=f"No exact address match found.",
                    severity="INFO"
                )
            update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)

    def find_matching_order(self, orders, target_genorderid, form_types, order_id,tfs_orderid):
        address_found = False
        address_list = []

        for order in orders:
            # order_address = clean_address(order.get('OrderGenId', ''))
            # cleaned_target = clean_address(target_genorderid)
            order_genid = order.get('OrderGenId', '')
            print(order.get('ProductDesc'))
            logger.log(
                    module="Redbell-find_matching_order",
                    order_id=hybrid_orderid,
                    action_type="Condition_check",
                    remarks=f"Product Description{order.get('ProductDesc')}",
                    severity="INFO"
                )
            if target_genorderid == order_genid:
                address_found = True
                print(f"Address Found {order['PropAddress']}for geniid{order['OrderGenId']}")

                logger.log(
                    module="Redbell-find_matching_order",
                    order_id=hybrid_orderid,
                    action_type="Condition_check",
                    remarks=f"Address Found {order['PropAddress']} for geniid{order['OrderGenId']}",
                    severity="INFO"
                )

                # Form matched
                if order.get('ProductDesc') in form_types:
                    print("Form matched")
                    print(order.get('OrderId'), order.get('ItemId'))
                    order_url = f"https://valuationops.homegenius.com/VendorPortal/EditReport?ItemId={order['ItemId']}&EntityType=Vendor"
                    print(order_url)

                    logger.log(
                    module="Redbell-find_matching_order",
                    order_id=hybrid_orderid,
                    action_type="Condition_check",
                    remarks=f"Form Matched",
                    severity="INFO"
                    )
                    return True, order, "matched"

                # Form not matched
                else:
                    print("Form not matched---New Type")

                    logger.log(
                    module="Redbell-find_matching_order",
                    order_id=hybrid_orderid,
                    action_type="Condition_check",
                    remarks=f"Form not Found --New Type {order.get('ProductDesc')}",
                    severity="INFO"
                    )
                    update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
                    return False, None, "form_not_matched"
                    

            else:
                print(f"Address Not Found {order.get('PropAddress')}")

                logger.log(
                    module="Redbell-find_matching_order",
                    order_id=hybrid_orderid,
                    action_type="Condition_check",
                    remarks=f"Address Not Found {order.get('PropAddress')}",
                    severity="INFO"
                    )
                address_list.append(order_genid)
        update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
        return False, None, "address_not_found"
        


    def redbell_launch_browser_and_open_form(self, order_url, session):
        # Navigate to order page
        self.driver.get("https://valuationops.homegenius.com/VendorPortal/InprogressOrder")
        self.driver.get(order_url)

        time.sleep(10)
    




def fill_form_multi(self, merged_json, order_id, form_config, session, page_urls,tfs_orderid): 
    key_expr_cache = {}
    value_cache = {}

    def get_keys_cached(key_expr):
        if key_expr not in key_expr_cache:
            key_expr_cache[key_expr] = re.findall(r"\['(.*?)'\]", key_expr)
        return key_expr_cache[key_expr]

    def extract_value_from_expr(expr: str):
        """
        Safely extract a value from merged_json sections based on the expression string.
        Returns None if the value is missing, never the literal expression.
        """

        if expr in value_cache:
            return value_cache[expr]

        # Define all possible data sources
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
            "rental_list1": rental_list1,
            "rental_list2": rental_list2,
            "rental_leased1": rental_leased1,
            "rental_leased2": rental_leased2,
            "adj_sold1": adj_sold1,
            "adj_sold2": adj_sold2,
            "adj_sold3": adj_sold3,
            "adj_list1": adj_list1,
            "adj_list2": adj_list2,
            "adj_list3": adj_list3
        }

        # Iterate through data sources to find matching prefix
        for prefix, source in data_sources.items():
            if expr.startswith(prefix):
                suffix = expr[len(prefix):]
                keys = re.findall(r"\['(.*?)'\]", suffix)

                # Use get_nested, default to None if not found
                value = get_nested(source, keys, None)

                # Convert numbers to strings for Selenium text input
                if isinstance(value, (int, float)):
                    value = str(value)

                value_cache[expr] = value
                if value is None:

                    logger.log(
                    module="Redbell-fill_form_multi",
                    order_id=hybrid_orderid,
                    action_type="Condition_check",
                    remarks=f"[extract_value_from_expr] Value for '{expr}' not found, defaulting to None",
                    severity="INFO"
                    )
                return value

        # If prefix not found, return None safely
        value_cache[expr] = None
        return expr

    field_actions = {
        "Textbox": data_filling_text,
        "Textbox_default": data_filling_text,
        "select_data": select_field,
        "select_default": select_field,
        "radiobutton_data": radio_btn_click,
        "radiobutton_default": radio_btn_click,
        "date_fill_javascript": javascript_excecuter_filling,
        "checkbox": single_checkbox,
    }

    try:
        sub_data, comp_data, adj_data, rental_data, sold1, sold2, sold3, list1, list2, list3 ,rental_list1,rental_list2,rental_leased1,rental_leased2,adj_sold1,adj_sold2,adj_sold3,adj_list1,adj_list2,adj_list3, prior1, prior2, prior3= extract_data_sections(merged_json)
        if sub_data is None:

            logger.log(
                    module="Redbell-fill_form_multi",
                    order_id=hybrid_orderid,
                    action_type="Condition_check",
                    remarks=f"'entry_data' missing or empty in merged_json",
                    severity="INFO"
                    )
            update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
            return False

        condition_data = generate_condition_data(sub_data, comp_data, adj_data, rental_data, sold1, sold2, sold3, list1, list2, list3,rental_list1,rental_list2,rental_leased1,rental_leased2,adj_sold1,adj_sold2,adj_sold3,adj_list1,adj_list2,adj_list3, prior1, prior2, prior3)
        saved_form = False

        for page in form_config.get("page", []):
            for section_name, controls in page.items():
                page_url = page_urls.get(section_name)
                if not page_url:

                    logger.log(
                    module="Redbell-fill_form_multi",
                    order_id=hybrid_orderid,
                    action_type="Condition_check",
                    remarks=f"URL not found for section: {section_name}",
                    severity="INFO"
                    )
                    continue


                logger.log(
                    module="Redbell-fill_form_multi",
                    order_id=hybrid_orderid,
                    action_type="Condition_check",
                    remarks=f"Navigating to section: {section_name} => {page_url}",
                    severity="INFO"
                    )
                self.driver.get(page_url)

                try:
                    WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                except Exception:

                    logger.log(
                    module="Redbell-fill_form_multi",
                    order_id=hybrid_orderid,
                    action_type="Exception",
                    remarks=f"Timeout waiting for page to load: {section_name}",
                    severity="INFO"
                    )

                for control in controls:
                    field_type = control.get("filedtype")
                    values = control.get("values", [])

                    if field_type == "save_data":
                        if not saved_form:
                            save_form(self.driver)



                            # for cookie in self.driver.get_cookies():
                            #     session.cookies.set(cookie['name'], cookie['value'])
                            # time.sleep(5)
                            saved_form = True
                        continue
                    if field_type == "save_data_adj":
                        if not saved_form:
                            save_form_adj(self.driver)

                            # for cookie in self.driver.get_cookies():
                            #     session.cookies.set(cookie['name'], cookie['value'])
                            # time.sleep(5)
                            saved_form = True
                        continue
                    if field_type == "checkbox_list":
                        for field in values:
                            if not (isinstance(field, list) and len(field) == 3):

                                logger.log(
                                    module="Redbell-fill_form_multi",
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

                                    logger.log(
                                    module="Redbell-fill_form_multi",
                                    order_id=hybrid_orderid,
                                    action_type="Condition-check",
                                    remarks=f"Checkboxes selected for {key_expr} with prefix {id_prefix}",
                                    severity="INFO"
                                    )
                            except Exception as e:

                                logger.log(
                                    module="Redbell-fill_form_multi",
                                    order_id=hybrid_orderid,
                                    action_type="Exception",
                                    remarks=f"Error selecting checkboxes for {key_expr}: {e}",
                                    severity="INFO"
                                    )
                        continue

                    if field_type == "repair_details_fill":
                        for field in values:
                            if not (isinstance(field, list) and len(field) == 3):

                                logger.log(
                                    module="Redbell-fill_form_multi",
                                    order_id=hybrid_orderid,
                                    action_type="Warning",
                                    remarks=f"Invalid repair_details_fill field: {field}",
                                    severity="INFO"
                                    )
                                continue
                            key_expr, _, _ = field
                            try:
                                value = extract_value_from_expr(key_expr)
                                if isinstance(value, list):
                                    fill_repair_details(self.driver, value)
                            except Exception as e:

                                logger.log(
                                    module="Redbell-fill_form_multi",
                                    order_id=hybrid_orderid,
                                    action_type="Exception",
                                    remarks=f"Error processing repair_details_fill: {e}",
                                    severity="ERROR"
                                )
                        continue

                    for field in values:
                        if not (isinstance(field, list) and len(field) == 3):

                            logger.log(
                                    module="Redbell-fill_form_multi",
                                    order_id=hybrid_orderid,
                                    action_type="Warning",
                                    remarks=f"Invalid field format: {field}",
                                    severity="INFO"
                                    )
                            continue

                        key_expr, xpath, mode = field
                        try:
                            value = extract_value_from_expr(key_expr)

                            if value in [None, ""]:
                                continue
                            # WebDriverWait(self.driver, 3).until(
                            #     EC.element_to_be_clickable((By.XPATH, xpath))
                            # )
                            action_func = field_actions.get(field_type)
                            if action_func:
                                action_func(self.driver, value, xpath, mode)
                            else:

                                logger.log(
                                    module="Redbell-fill_form_multi",
                                    order_id=hybrid_orderid,
                                    action_type="Warning",
                                    remarks=f"Unknown field type: {field_type}",
                                    severity="INFO"
                                    )
                        except Exception as e:
                            logger.log(
                            module="Redbell-fill_form_multi",
                            order_id=hybrid_orderid,
                            action_type="Exception",
                            remarks=f"Exception filling field {key_expr}: {e}",
                            severity="INFO"
                            )


        if saved_form:
            #update_order_status(order_id, "In Progress", "Entry", "Filled")
            logger.log(
                            module="Redbell-fill_form_multi",
                            order_id=hybrid_orderid,
                            action_type="Condition-check",
                            remarks=f"Form saved.",
                            severity="INFO"
                            )
            return True
        else:
            #update_order_status(order_id, "In Progress", "Entry", "Failed")
            logger.log(
                            module="Redbell-fill_form_multi",
                            order_id=hybrid_orderid,
                            action_type="Condition-check",
                            remarks=f"Form not saved.",
                            severity="INFO"
                            )
            return False

    except Exception as e:

        logger.log(
            module="Redbell-fill_form_multi",
            order_id=hybrid_orderid,
            action_type="Exception",
            remarks=f"Critical error in fill_form_multi: {e}",
            severity="ERROR"
        )
        logger.log(
                            module="Redbell-fill_form_multi",
                            order_id=hybrid_orderid,
                            action_type="Exception",
                            remarks=f"Critical error in fill_form_multi: {e}",
                            severity="INFO"
                            )
        #update_order_status(order_id, "In Progress", "Entry", "Failed")
        return False







# def upload_file_js(driver, input_id, file_path):
#     try:
#         input_elem = driver.find_element(By.ID, input_id)
        
#         # Make input visible via JS (if hidden)
#         driver.execute_script("""
#             arguments[0].style.display = 'block'; 
#             arguments[0].style.visibility = 'visible'; 
#             arguments[0].style.height = '1px';
#             arguments[0].style.width = '1px';
#             arguments[0].style.opacity = 1;
#         """, input_elem)
        
#         # Clear existing value
#         driver.execute_script("arguments[0].value = '';", input_elem)

#         # Send file path
#         input_elem.send_keys(file_path)

#         # Wait shortly for input to register file
#         time.sleep(1)

#         # Check if input value contains file name
#         input_value = driver.execute_script("return arguments[0].value;", input_elem)
#         if not input_value or input_value.strip() == "":
#             print(f"[✗] Input '{input_id}' did not register file after upload.")
#             return False
        
#         # Optionally hide input back
#         driver.execute_script("arguments[0].style.display = 'none';", input_elem)

#         print(f"[✓] Uploaded file '{file_path}' to input '{input_id}' (value: {input_value})")
#         return True

#     except Exception as e:
#         print(f"[✗] Failed to upload '{file_path}' to '{input_id}': {e}")
#         return False

def upload_file_js(driver, input_id, file_path):
    """
    Uploads a file using two methods:
    Method 1: Direct Selenium send_keys after making input visible.
    Method 2: Fallback to portal's internal uploadDocument JS function.
    """
    # --- Method 1: Direct Selenium Upload ---
    try:
        input_elem = driver.find_element(By.ID, input_id)
        
        # Make input visible via JS
        driver.execute_script("""
            arguments[0].style.display = 'block'; 
            arguments[0].style.visibility = 'visible'; 
            arguments[0].style.height = '1px';
            arguments[0].style.width = '1px';
            arguments[0].style.opacity = 1;
            arguments[0].style.position = 'absolute';
        """, input_elem)
        
        # Clear and Send Keys
        driver.execute_script("arguments[0].value = '';", input_elem)
        input_elem.send_keys(file_path)
        time.sleep(2)

        # Quick check if it registered
        input_value = driver.execute_script("return arguments[0].value;", input_elem)
        if input_value and input_value.strip() != "":
            logger.log(
                module="Redbell-upload_file_js",
                order_id=hybrid_orderid,
                action_type="Document-upload-success",
                remarks=f"[✓] Method 1: Uploaded {file_path} to {input_id}",
                severity="INFO"
            )
            return True
            
        logger.log(
            module="Redbell-upload_file_js",
            order_id=hybrid_orderid,
            action_type="Warning",
            remarks=f"Method 1 did not register value for {input_id}. Trying Method 2 fallback.",
            severity="INFO"
        )

    except Exception as e:
        logger.log(
            module="Redbell-upload_file_js",
            order_id=hybrid_orderid,
            action_type="Warning",
            remarks=f"Method 1 exception for {input_id}: {e}. Trying Method 2 fallback.",
            severity="INFO"
        )

    # # --- Method 2: Fallback to Portal JS ---
    try:
        # Attempt to trigger portal's internal function
        driver.execute_script(f"if(typeof uploadDocument === 'function') {{ uploadDocument('{input_id}'); }}")
        time.sleep(1)

        input_elem = driver.find_element(By.ID, input_id)
        input_elem.send_keys(file_path)
        time.sleep(2)

        # Final verification
        input_value = driver.execute_script("return arguments[0].value;", input_elem)
        if input_value and input_value.strip() != "":
            logger.log(
                module="Redbell-upload_file_js",
                order_id=hybrid_orderid,
                action_type="Document-upload-success",
                remarks=f"[✓] Method 2: Uploaded {file_path} to {input_id}",
                severity="INFO"
            )
            return True
        else:
            logger.log(
                module="Redbell-upload_file_js",
                order_id=hybrid_orderid,
                action_type="Document-upload-failure",
                remarks=f"[✗] Both upload methods failed for {input_id}.",
                severity="INFO"
            )
            return False

    except Exception as e:
        logger.log(
            module="Redbell-upload_file_js",
            order_id=hybrid_orderid,
            action_type="Document-upload-failure",
            remarks=f"[✗] Method 2 exception for {input_id}: {e}",
            severity="INFO"
        )
        return False




def upload_files_for_order(self, order_id: int, upload_page_url: str ,tfs_orderid: str) -> bool:
    data = fetch_upload_data(self, order_id)
    if not data:
        update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
        
        return False

    documents = data.get("documents", [])
    comparables_folder = data.get("comparables_folder", "")

    file_paths = {}
  

    # Comp PDFs (s1–s3, a1–a3)
    if os.path.exists(comparables_folder):
        for fname in os.listdir(comparables_folder):
            full_path = os.path.join(comparables_folder, fname)
            fname_lower = fname.lower()

            if not fname_lower.endswith(".pdf"):
                continue

            if match := re.match(r"s([1-3])\.pdf", fname_lower):
                file_paths[f"MLSPdfIdSoldComp{match.group(1)}"] = full_path
            elif match := re.match(r"a([1-3])\.pdf", fname_lower):
                file_paths[f"MLSPdfIdListedComp{match.group(1)}"] = full_path
    else:
        update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
        #print("Comparables folder not found!")
        logger.log(
        module="Redbell-upload_files_for_order",
        order_id=hybrid_orderid,
        action_type="Condition-check",
        remarks=f"Comparables folder not found!",
        severity="INFO"
        )
        return False
    
    # Subject PDFs
    for doc in documents:
        doc_type = doc.get("type", "").lower()
        doc_path = doc.get("path")
        if doc_type == "tax":
            file_paths["TaxPdfIdSubject"] = doc_path
        elif doc_type == "mls_tax":
            file_paths["MLSPdfIdSubject"] = doc_path  

    # Navigate to upload page
    self.driver.get(upload_page_url)
    time.sleep(3)

    # Upload PDFs and verify each upload
    for input_id, file_path in file_paths.items():
        if not os.path.exists(file_path):
            #print(f"File not found: {file_path}")
            logger.log(
            module="Redbell-upload_files_for_order",
            order_id=hybrid_orderid,
            action_type="Condition-check",
            remarks=f"File not found: {file_path}",
            severity="INFO"
            )
            update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
            return False
        
        success = upload_file_js(self.driver, input_id, file_path)
        if not success:
            update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
            return False
        
        time.sleep(0.5)

    # All files uploaded and verified
    return True



def count_non_subject_photos(self):
    from selenium.common.exceptions import StaleElementReferenceException
    subject_labels = set()
    try:
        tables = self.driver.find_elements(By.XPATH, "//div[@id='RequiedPhotosDetail']//table[@id='requiredphototable']")
        for table in tables:
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                try:
                    text = row.text.strip().lower()
                    if text:
                        subject_labels.add(text)
                except StaleElementReferenceException:
                    continue

        photo_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class,'photo-thumbnail')]//img")
        count = 0
        #print("Checking uploaded photo labels:")
        for img in photo_elements:
            try:
                alt = (img.get_attribute("alt") or "").strip().lower()
                aria = (img.get_attribute("aria-label") or "").strip().lower()
                label = alt or aria
                #print(f"   → ALT: {alt}, ARIA: {aria}")
                if label in subject_labels:
                    continue
                count += 1
            except StaleElementReferenceException:
                continue
        return count
    except Exception as e:

        logger.log(
            module="Redbell-count_non_subject_photos",
            order_id=hybrid_orderid,
            action_type="Exception",
            remarks=f"Error in count_non_subject_photos: {e}",
            severity="INFO"
        )
        return 0

def get_required_non_subject_labels(self):
    from selenium.common.exceptions import StaleElementReferenceException
    labels = set()
    try:
        tables = self.driver.find_elements(By.XPATH, "//div[@id='RequiedPhotosDetail']//table[@id='requiredphototable']")
        for table in tables:
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                try:
                    label = row.text.strip()
                    if label and "subject" not in label.lower():
                        labels.add(label.lower())
                except StaleElementReferenceException:
                    continue
        return labels
    except Exception as e:

        logger.log(
            module="Redbell-get_required_non_subject_labels",
            order_id=hybrid_orderid,
            action_type="Exception",
            remarks=f"Error in get_required_non_subject_labels: {e}",
            severity="INFO"
        )
        return set()


def delete_non_subject_photos(self):
    from selenium.common.exceptions import StaleElementReferenceException
    wait = WebDriverWait(self.driver, 20)

    try:
        # Wait for at least one photo item
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.qq-upload-success")))
    except TimeoutException:
        #print("No photos found.")
        logger.log(
            module="Redbell-delete_non_subject_photos",
            order_id=hybrid_orderid,
            action_type="Exception",
            remarks=f"No photos found.",
            severity="INFO"
            )
        return False

    #print("Scanning uploaded photos...")
    try:
        photo_items = self.driver.find_elements(By.CSS_SELECTOR, "li.qq-upload-success")
        non_subject_count = 0

        for item in photo_items:
            try:
                # Each photo dropdown
                dropdown_el = item.find_element(By.CSS_SELECTOR, "select.qq-edit-filetype")
                dropdown = Select(dropdown_el)

                selected_text = dropdown.first_selected_option.text.strip()
                # print("Dropdown:", selected_text)

                # If not Subject → tick checkbox
                if "Subject" not in selected_text:
                    checkbox = item.find_element(By.CSS_SELECTOR, "input.qq-upload-checkbox")

                    if not checkbox.is_selected():
                        checkbox.click()
                        non_subject_count += 1
                        logger.log(
                        module="Redbell-delete_non_subject_photos",
                        order_id=hybrid_orderid,
                        action_type="Condition-check",
                        remarks=f" Marked NON-Subject photo: {selected_text}",
                        severity="INFO"
                        )
            except (NoSuchElementException, StaleElementReferenceException):
                continue

        if non_subject_count == 0:
            #print("No non-subject photos found.")
            logger.log(
                        module="Redbell-delete_non_subject_photos",
                        order_id=hybrid_orderid,
                        action_type="Condition-check",
                        remarks=f"No non-subject photos found.",
                        severity="INFO"
                        )
            return False

        #print(f"Total photos to delete: {non_subject_count}")
        logger.log(
                        module="Redbell-delete_non_subject_photos",
                        order_id=hybrid_orderid,
                        action_type="Condition-check",
                        remarks=f"Total photos to delete: {non_subject_count}",
                        severity="INFO"
                        )
        # Click Delete Photos button
        try:
            delete_btn = wait.until(EC.element_to_be_clickable((By.ID, "trigger-delete")))
            delete_btn.click()
            #print("Delete button clicked.")
            logger.log(
                        module="Redbell-delete_non_subject_photos",
                        order_id=hybrid_orderid,
                        action_type="Confirmation",
                        remarks=f"Delete button clicked.",
                        severity="INFO"
                        )
        except TimeoutException:
            #print(" Delete Photos button not found.")
            logger.log(
                        module="Redbell-delete_non_subject_photos",
                        order_id=hybrid_orderid,
                        action_type="Exception",
                        remarks=f" Delete Photos button not found.",
                        severity="INFO"
                        )
            return False

        # Handle confirmation popup (if exists)
        try:
            confirm_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".confirm, .btn-primary"))
            )
            confirm_btn.click()
            #print("✔ Confirmed delete.")
            logger.log(
                        module="Redbell-delete_non_subject_photos",
                        order_id=hybrid_orderid,
                        action_type="Confirmation",
                        remarks=f"Confirmed delete.",
                        severity="INFO"
                        )
        except TimeoutException:
            #print("⚠ No confirmation popup found (maybe auto-deleted).")
            logger.log(
                        module="Redbell-delete_non_subject_photos",
                        order_id=hybrid_orderid,
                        action_type="Exception",
                        remarks=f"No confirmation popup found (maybe auto-deleted).",
                        severity="INFO"
                        )

        return True
    except Exception as e:
        import traceback

        logger.log(
            module="Redbell-delete_non_subject_photos",
            order_id=hybrid_orderid,
            action_type="Exception",
            remarks=f"Error in delete_non_subject_photos: {traceback.format_exc()}",
            severity="ERROR"
        )
        return False

def upload_photos_to_order(self, comparables_folder, photos_url, ProductDesc, rental_folder=None) -> bool:
    missing = []
    try:
        self.driver.get(photos_url)
        time.sleep(3)
        # --- Step 0: FIRST delete old non-subject photos ---
        result = delete_non_subject_photos(self)

        if result:
            #print("Non-subject photos deleted successfully!")
            logger.log(
                    module="Redbell-delete_non_subject_photos",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"Non-subject photos deleted successfully!",
                    severity="INFO"
                    )
        else:
            #print("No deletion performed.")
            logger.log(
                    module="Redbell-delete_non_subject_photos",
                    order_id=hybrid_orderid,
                    action_type="Condition-check",
                    remarks=f"No deletion performed.",
                    severity="INFO"
                    )
         # --- Step 1: Click "Location Map" button to load map ---
        try:
            location_map_btn = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@title='Refresh location map']"))
            )
            self.driver.execute_script("arguments[0].click();", location_map_btn)
            #print("Location Map button clicked.")
            logger.log(
            module="Redbell-upload_photos_to_order",
            order_id=hybrid_orderid,
            action_type="Try",
            remarks=f"Location Map button clicked.",
            severity="INFO"
            )
            # Optional: wait for the map div to appear
            WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.ID, "location-map"))
            )
            #print("Location Map loaded.")
            logger.log(
            module="Redbell-upload_photos_to_order",
            order_id=hybrid_orderid,
            action_type="Try",
            remarks=f"Location Map loaded.",
            severity="INFO"
            )
        except Exception as map_err:
            #print("Location Map button not found or failed to load:", map_err)
            logger.log(
            module="Redbell-upload_photos_to_order",
            order_id=hybrid_orderid,
            action_type="Exception",
            remarks=f"Location Map button not found or failed to load: {map_err} ",
            severity="INFO"
            )
        # Step 0: Check if any non-subject photo is required
        required_non_subject_labels = get_required_non_subject_labels(self)
        if not required_non_subject_labels:
            #print(" No non-subject photos required for upload.")
            logger.log(
            module="Redbell-upload_photos_to_order",
            order_id=hybrid_orderid,
            action_type="Condition-check",
            remarks=f"No non-subject photos required for upload. ",
            severity="INFO"
            )
            return False

        if not os.path.exists(comparables_folder):
            #print(" Comparables folder missing.")
            logger.log(
            module="Redbell-upload_photos_to_order",
            order_id=hybrid_orderid,
            action_type="Condition-check",
            remarks=f"Comparables folder missing. ",
            severity="INFO"
            )
            return False
        if rental_folder and not os.path.exists(rental_folder):
            rental_folder = None

        label_to_file_map = {}

        def add_photos_from_folder(folder, is_rental=False):
            for fname in os.listdir(folder):
                if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
                    continue
                match = re.match(r'([aslrb])([1-3])\.(jpg|jpeg|png)', fname.lower())
                if match:
                    prefix, idx, _ = match.groups()
                    label = {
                        'a': f"Listing Comp {idx}",
                        's': f"Sold Comp {idx}",
                        'l': f"Leased Comp {idx}",
                        'r': f"Active Comp {idx}"
                    }.get(prefix)
                    if label:
                        key = label.lower()
                        if is_rental:
                            key = f"{key}|rental"
                        label_to_file_map[key] = os.path.join(folder, fname)

        add_photos_from_folder(comparables_folder)
        if rental_folder and "Rental" in ProductDesc:
            add_photos_from_folder(rental_folder, is_rental=True)

        labels_sorted = sorted(label_to_file_map.keys())
        expected_labels = [k.replace("|rental", "").title() for k in labels_sorted]

        # Step 1: Detect already present labels
        photo_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class,'photo-thumbnail')]//img")
        present_labels = set()
        for img in photo_elements:
            alt = (img.get_attribute("alt") or "").strip().lower()
            aria = (img.get_attribute("aria-label") or "").strip().lower()
            for lbl in expected_labels:
                if lbl.lower() in alt or lbl.lower() in aria:
                    present_labels.add(lbl.lower())

        if all(lbl.lower() in present_labels for lbl in expected_labels):
            #print(" All non-subject photos already uploaded. Skipping upload.")
            logger.log(
            module="Redbell-upload_photos_to_order",
            order_id=hybrid_orderid,
            action_type="Condition-check",
            remarks=f"All non-subject photos already uploaded. Skipping upload.",
            severity="INFO"
            )
            return False

        # Step 2: Count before upload
        photos_before = count_non_subject_photos(self)
        #print(f" Non-subject photos before upload: {photos_before}")
        logger.log(
            module="Redbell-upload_photos_to_order",
            order_id=hybrid_orderid,
            action_type="Condition-check",
            remarks=f"Non-subject photos before upload: {photos_before}",
            severity="INFO"
            )

        # Step 3: Upload only missing
        for label_key in labels_sorted:
            file_path = label_to_file_map[label_key]
            label = label_key.replace("|rental", "")
            if any(label.lower() in lbl for lbl in present_labels):
                print(f" Skipping already uploaded: {label.title()}")
                continue

            current_select_count = len(self.driver.find_elements(By.NAME, "fileType"))

            file_input_xpath = "(//input[@type='file' and @name='qqfile'])[1]"
            file_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, file_input_xpath))
            )
            file_input.send_keys(file_path)

            WebDriverWait(self.driver, 10).until(
                lambda d: len(d.find_elements(By.NAME, "fileType")) > current_select_count
            )
            all_selects = self.driver.find_elements(By.NAME, "fileType")
            select_element = all_selects[-1]

            if select_element.get_attribute("disabled"):
                self.driver.execute_script("arguments[0].removeAttribute('disabled');", select_element)

            photo_names_select = Select(select_element)
            options_text = [opt.text.strip() for opt in photo_names_select.options]

            base_name = label.title()
            asterisk_name = f"* {base_name}"

            if asterisk_name in options_text:
                photo_names_select.select_by_visible_text(asterisk_name)
            elif base_name in options_text:
                photo_names_select.select_by_visible_text(base_name)
            else:
                #print(f" No matching option for label: {base_name}")
                logger.log(
                module="Redbell-upload_photos_to_order",
                order_id=hybrid_orderid,
                action_type="Condition-check",
                remarks=f" No matching option for label: {base_name}",
                severity="INFO"
                )
                return False

            #print(f" Uploaded: {base_name}")
            logger.log(
                module="Redbell-upload_photos_to_order",
                order_id=hybrid_orderid,
                action_type="Condition-check",
                remarks=f" Uploaded: {base_name}",
                severity="INFO"
                )
            time.sleep(1)

        # Step 4: Trigger upload
        upload_button = WebDriverWait(self.driver, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//*[@id='trigger-upload']"))
        )
        self.driver.execute_script("arguments[0].click();", upload_button)

        WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//img[contains(@src,'blob:') or contains(@src,'http')]"))
        )

        # Step 5: Wait and recheck UI
        #print(" Waiting for upload to reflect on UI...")
        logger.log(
                module="Redbell-upload_photos_to_order",
                order_id=hybrid_orderid,
                action_type="Condition-check",
                remarks=f" Waiting for upload to reflect on UI...",
                severity="INFO"
                )
        time.sleep(5)
        photos_after = count_non_subject_photos(self)

        actual_uploaded = photos_after - photos_before
        #print(f" Non-subject photos after upload: {photos_after}")
        #print(f" Actually uploaded during this session: {actual_uploaded}")

        # Step 6: Final verification using Required Photos section
        remaining_required = get_required_non_subject_labels(self)
        #print(" Remaining required non-subject labels:", remaining_required)
        logger.log(
                module="Redbell-upload_photos_to_order",
                order_id=hybrid_orderid,
                action_type="Condition-check",
                remarks=f" Non-subject photos after upload: {photos_after}",
                severity="INFO"
                )
        logger.log(
                module="Redbell-upload_photos_to_order",
                order_id=hybrid_orderid,
                action_type="Condition-check",
                remarks=f"  Actually uploaded during this session: {actual_uploaded}",
                severity="INFO"
                )
        logger.log(
                module="Redbell-upload_photos_to_order",
                order_id=hybrid_orderid,
                action_type="Condition-check",
                remarks=f" Remaining required non-subject labels: {remaining_required}",
                severity="INFO"
                )

        #missing = []
        for lbl in expected_labels:
            if lbl.lower() in remaining_required:
                missing.append(lbl)

        if not missing:
            #print("All non-subject photos uploaded successfully (verified via 'Required Photos' section).")
            logger.log(
                module="Redbell-upload_photos_to_order",
                order_id=hybrid_orderid,
                action_type="Condition-check",
                remarks=f" All non-subject photos uploaded successfully (verified via 'Required Photos' section).",
                severity="INFO"
                )

            return True
        else:
            #print("Still missing the following non-subject photos:")
            logger.log(
                module="Redbell-upload_photos_to_order",
                order_id=hybrid_orderid,
                action_type="Condition-check",
                remarks=f"Still missing the following non-subject photos:",
                severity="INFO"
                )
            for m in missing:
                #print("   -", m)
                logger.log(
                module="Redbell-upload_photos_to_order",
                order_id=hybrid_orderid,
                action_type="Condition-check",
                remarks=f" missing  - {m}",
                severity="INFO"
                )
            return False

    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        #print(" Upload failed with error:", e)
        for m in missing:
                #print("   -", m)
                logger.log(
                module="Redbell-upload_photos_to_order",
                order_id=hybrid_orderid,
                action_type="Condition-check",
                remarks=f"Upload failed with error: {e} - missing {m}",
                severity="INFO"
                )
        if not missing:
            logger.log(
                module="Redbell-upload_photos_to_order",
                order_id=hybrid_orderid,
                action_type="Condition-check",
                remarks=f"Upload failed with error: {e}",
                severity="INFO"
                )
        

        logger.log(
            module="Redbell-upload_photos_to_order",
            order_id=hybrid_orderid,
            action_type="Exception",
            remarks=f"RedBell photo upload exception: {error_msg}",
            severity="ERROR"
        )
        return False




def build_url(base_url, item_id, order_id, page):
    return f"{base_url}?ItemId={item_id}&OrderId={order_id}&ActivePage={page}"





def redbell_formopen_fill(self, order, session=None, merged_json=None, order_details=None, order_id=None,tfs_orderid=None,is_qc=None):
    #order_id="132"
    ProductDesc = order.get('ProductDesc', '').strip()
    item_id = order.get('ItemId')
    order_id_url = order.get('OrderId')

    base_url = env.BASE_URL_ENTRY
    
    researchpad_data_retrival_url=env.RESEARCHPAD_DATA_URL
    if ProductDesc=="Exterior BPO" or ProductDesc=="5 Day Exterior BPO"  or  ProductDesc=="5 Day Interior BPO" or ProductDesc=="5 Day Exterior Appraiser Reconciled BPO" or ProductDesc=="3 Day Exterior BPO"  or  ProductDesc=="3 Day Interior BPO" or ProductDesc=="Exterior Enhanced BPO":
         # Exterior URLs
        page_urls = {
            "SubjectHistoryAdj": build_url(base_url, item_id, order_id_url, "Subject%20History"),
            "NeighborhoodInfoAdj": build_url(base_url, item_id, order_id_url, "Neighborhood%20Info"),
            "ComparablesAdj": build_url(base_url, item_id, order_id_url, "Comparables"),
            "Photos": build_url(base_url, item_id, order_id_url, "Photos"),
            "Repairs": build_url(base_url, item_id, order_id_url, "Repairs"),
            "Comments": build_url(base_url, item_id, order_id_url, "Comments"),
            "Price Opinion": build_url(base_url, item_id, order_id_url, "Price%20Opinion"),
        }
        if ProductDesc == "Exterior Enhanced BPO":
            config_path = 'json/redbelljson/Redbell_Exterior_Enhanced_Bpo.json'
        else:
            config_path = 'json/redbelljson/Redbell_Exterior.json'

    elif ProductDesc=="Interior BPO":
        page_urls = {
            "SubjectHistoryAdj": build_url(base_url, item_id, order_id_url, "Subject%20History"),
            "NeighborhoodInfoAdj": build_url(base_url, item_id, order_id_url, "Neighborhood%20Info"),
            "ComparablesAdj": build_url(base_url, item_id, order_id_url, "Comparables"),
            "Photos": build_url(base_url, item_id, order_id_url, "Photos"),
            "Update": build_url(base_url, item_id, order_id_url, "BPOMITRepair"),
            "Comments": build_url(base_url, item_id, order_id_url, "Comments"),
            "Price Opinion": build_url(base_url, item_id, order_id_url, "Price%20Opinion"),
        }
        config_path = 'json/redbelljson/Redbell_Interior_BPO.json'
    elif "Rental" in ProductDesc:

        # Rental URLs
        page_urls = {
            "SubjectHistoryAdj": build_url(base_url, item_id, order_id_url, "SubjectHistoryAdj"),
            "NeighborhoodInfoAdj": build_url(base_url, item_id, order_id_url, "NeighborhoodInfoAdj"),
            "ComparablesAdj": build_url(base_url, item_id, order_id_url, "ComparablesAdj"),
            "Photos": build_url(base_url, item_id, order_id_url, "Photos"),
            "Repairs": build_url(base_url, item_id, order_id_url, "Repairs"),
            "Rental Comparables": build_url(base_url, item_id, order_id_url, "Rental%20Comparables"),
            "Comments": build_url(base_url, item_id, order_id_url, "Comments"),
            "Price Opinion": build_url(base_url, item_id, order_id_url, "Price%20Opinion"),
        }

        config_path = 'json/redbelljson/Redbell_Rental.json'

    else:
        logger.log(
                module="Redbell-redbell_formopen_fill",
                order_id=hybrid_orderid,
                action_type="Condition-check",
                remarks=f"No matching config path for ProductDesc: {ProductDesc}",
                severity="INFO"
                )


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
    sub_data, comp_data, adj_data, rental_data,sold1,sold2,sold3, list1, list2, list3,rental_list1,rental_list2,rental_leased1,rental_leased2,adj_sold1,adj_sold2,adj_sold3,adj_list1,adj_list2,adj_list3, prior1, prior2, prior3 = extract_data_sections(merged_json)
    condition_data = generate_condition_data(sub_data, comp_data, adj_data, rental_data,sold1,sold2,sold3, list1, list2, list3,rental_list1,rental_list2,rental_leased1,rental_leased2,adj_sold1,adj_sold2,adj_sold3,adj_list1,adj_list2,adj_list3, prior1, prior2, prior3)
    if "entry_data" in merged_json and merged_json["entry_data"]:
        merged_json["entry_data"][0]["condition_data"] = condition_data

    #print(merged_json)    
    logger.log(
                module="Redbell-redbell_formopen_fill",
                order_id=hybrid_orderid,
                action_type="Condition-check",
                remarks=f"merged_json: {merged_json}",
                severity="INFO"
                )

    try:
        for page_key, url in page_urls.items():
            # Optional: Skip unwanted sections
            # if page_key == "ComparablesAdj":
            #     continue


            logger.log(
                module="Redbell-redbell_formopen_fill",
                order_id=hybrid_orderid,
                action_type="Condition-check",
                remarks=f"Loading page: {page_key} -> {url}",
                severity="INFO"
                )
            redbell_formopen_fill
            self.driver.get(url)

            # Explicit wait: waits until the body or a unique element is loaded
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))  # Replace with unique tag if needed
                )

                logger.log(
                module="Redbell-redbell_formopen_fill",
                order_id=hybrid_orderid,
                action_type="Try",
                remarks=f"Page {page_key} loaded successfully.",
                severity="INFO"
                )
            except Exception as e:

                logger.log(
                module="Redbell-redbell_formopen_fill",
                order_id=hybrid_orderid,
                action_type="Exception",
                remarks=f"Timeout waiting for page {page_key} to load: {e}",
                severity="INFO"
                )
                #update_order_status(order_id, "In Progress", "Entry", "Failed")
                continue  # optionally skip to next page

            # Call fill_form_multi for just this page
            form_fill=fill_form_multi(self, merged_json, order_id_url, form_config, session, {page_key: url},tfs_orderid)
            time.sleep(2)

    except Exception as e:

        logger.log(
                module="Redbell-redbell_formopen_fill",
                order_id=hybrid_orderid,
                action_type="Exception",
                remarks=f"Error while navigating and filling forms: {e}",
                severity="INFO"
                )
        #update_order_status(order_id, "In Progress", "Entry", "Failed")
        return

    try:
        comparables_url = page_urls["ComparablesAdj"]
        uploda_files=upload_files_for_order(self, order_id, comparables_url,tfs_orderid)

        data = fetch_upload_data(self, order_id)
        if not data:

            logger.log(
                module="Redbell-redbell_formopen_fill",
                order_id=hybrid_orderid,
                action_type="Try",
                remarks=f"No upload data found for order {order_id}",
                severity="INFO"
                )
            update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
            return

        comparables_folder = data.get("comparables_folder")
        rental_folder = data.get("rental_folder")
        photos_url = page_urls["Photos"]

        if isinstance(comparables_folder, str) and comparables_folder.strip():
            upload_photos=upload_photos_to_order(self, comparables_folder, photos_url,ProductDesc, rental_folder)
        else:

            logger.log(
                module="Redbell-redbell_formopen_fill",
                order_id=hybrid_orderid,
                action_type="Condition-check",
                remarks=f"Comparables folder is missing or invalid for order {order_id}: {comparables_folder!r}",
                severity="INFO"
                )
            update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
        # Check if all 3 are True
        if form_fill and uploda_files and upload_photos:

            logger.log(
                module="Redbell-redbell_formopen_fill",
                order_id=hybrid_orderid,
                action_type="Condition-check",
                remarks=f"All form filling and upload functions completed successfully.",
                severity="INFO"
                )
            
            if is_qc :   #qc order
                logger.log(module="TFS_Status_Change",order_id=hybrid_orderid,action_type="Status_change",remarks="QC order status change ",severity="INFO")
                tfs_statuschange(tfs_orderid , "82", "17", "14")
            else:
                logger.log(module="TFS_Status_Change",order_id=hybrid_orderid,action_type="Status_change",remarks="fresh or redo order status change ",severity="INFO")
                tfs_statuschange(tfs_orderid , "26", "5", "20")

            update_order_status(hybrid_orderid, "In Progress", "Entry", "Filled",hybrid_token)
            
        else:

            logger.log(
                module="Redbell-redbell_formopen_fill",
                order_id=hybrid_orderid,
                action_type="Condition-check",
                remarks=f"One or more functions failed: form_fill={form_fill}, uploda_files={uploda_files}, upload_photos={upload_photos}",
                severity="INFO"
                )
            update_order_status(order_id, "In Progress", "Entry", "Failed",hybrid_token)
    except Exception as e:

        logger.log(
                module="Redbell-redbell_formopen_fill",
                order_id=hybrid_orderid,
                action_type="Exception",
                remarks=f"Error during photo upload steps: {e}",
                severity="INFO"
                )
        update_order_status(hybrid_orderid, "In Progress", "Entry", "Failed",hybrid_token)
        return

