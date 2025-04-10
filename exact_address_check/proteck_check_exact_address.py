import json
import re
import logging
import ssl
import requests
from bs4 import BeautifulSoup

import json
import re
import logging
from bs4 import BeautifulSoup
import requests

def find_matching_order(orders, target_address, form_types, order_id, driver):
    '''Function to match the address and form type for ProTeck orders'''
    try:
        # Get the page source from Selenium
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract JSON data from the page (assuming it's in a script tag)
        script_tag = soup.find('script', {'type': 'application/json'})
        if script_tag:
            open_data_json = json.loads(script_tag.string)  # Parse JSON string from script tag
        else:
            logging.error("JSON data not found in page.")
            return [], False, None  # Return empty list if no data found

        # Count how many orders are in progress
        orders_in_progress = len(open_data_json)
        orders_list = []  # List to store orders
        address_list = []  # List to store addresses
        matched = False  # Variable to indicate if an address is matched
        status = None  # Variable to store the status of the matched order

        if orders_in_progress > 0:
            logging.info(f"Orders in progress: {orders_in_progress}")
            
            # Loop through the orders to collect them
            for open_subject in open_data_json:
                status_type = open_subject.get('statusType', '')

                # Only process orders with "Pending" or "NeedsRevision" status
                if 'Pending' in status_type or 'NeedsRevision' in status_type:
                    order_data = {
                        'caseNumber': open_subject.get('caseNumber'),
                        'statusType': status_type,
                        'orderId': open_subject.get('orderId'),
                    }
                    orders_list.append(order_data)  # Append order to list

                    # Clean the address
                    address = open_subject.get('address', {})
                    address1 = address.get('address1', '').replace(" ", "").upper()
                    address2 = address.get('address2', '')
                    address3 = address.get('suite', '')
                    city = address.get('city', '')
                    state = address.get('state', '')
                    zipcode = address.get('zip', '')
                    
                    # Construct and clean the full address
                    full_address = f"{address1} {address2} {address3} {city} {state} {zipcode}"
                    cleaned_address = re.sub(r'[\"\'\-,:/]', '', full_address)
                    cleaned_address = re.sub(r'\s+', '', cleaned_address).upper()
                    address_list.append(cleaned_address)  # Append cleaned address to list

            # Now check if any order matches the target address
            for order, cleaned_address in zip(orders_list, address_list):
                if target_address == cleaned_address:
                    matched = True
                    status = order['statusType']
                    break  # Exit after finding the first match

            return orders_list, matched, status  # Return the orders list, match status, and status

        else:
            logging.info("No orders in portal.")
            return [], False, None  # Return empty list and False if no orders are in the portal

    except Exception as err:
        logging.error(f"Exception occurred while retrieving orders and addresses: {err}")
        return [], False, None  # Return empty list and False in case of error
