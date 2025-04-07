import re
import logging
from ssl import Options
import webbrowser

from check_and_form_open.redbell_check_and_form_open import check_and_open_form
from utils.helper import clean_address,get_order_address_from_assigned_order  # For opening the form link
def redbell_check_exact_address( orders, session, merged_json=None):
    """
    Checks if the address from the order matches exactly with any of the portal orders.
    If found, opens the corresponding form.
    """
    try:
        for order in orders:  # Iterate through each order in the list
                # Check if order is a dictionary and contains 'order_id'
                if isinstance(order, dict):
                    order_id = order.get("order_id")  # Get the 'order_id' for the current order

                    if not order_id:
                        print("Order ID missing.")
                        continue  # Skip this order if the order_id is missing
                    
                

                # Step 1: Get and clean address from API
                tfs_address_raw = get_order_address_from_assigned_order(order_id)
                cleaned_tfs_address = clean_address(tfs_address_raw)

                logging.info(f"Cleaned TFS address: {cleaned_tfs_address}")

                # Step 2: Loop through portal orders and compare cleaned addresses
                matched_orders = []
                for order in orders:
                    prop_address_raw = order.get("PropAddress", "")
                    cleaned_portal_address = clean_address(prop_address_raw)

                    if cleaned_tfs_address == cleaned_portal_address:
                        print(f"Address matched: {cleaned_portal_address}")
                        logging.info(f"Address matched: {cleaned_portal_address}")
                        matched_orders.append(order)

                # Step 3: Open form if match found
                if matched_orders:
                    check_and_open_form(matched_orders, session, merged_json)
                else:
                    print("Exact address not found in portal orders.")
                    logging.info("Exact address not found.")

    except Exception as e:
        logging.error(f"Error during exact address check: {e}")
        print(f"Exception occurred: {e}")