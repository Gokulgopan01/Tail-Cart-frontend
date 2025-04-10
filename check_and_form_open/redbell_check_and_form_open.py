import re
import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


from exact_address_check.redbell_check_exact_address import find_matching_order
from launch_browser_and_open_form.redbell_launch_browser_and_open_form import redbell_launch_browser_and_open_form
from utils.helper import clean_address

# def formopen_fill(orders, session, merged_json, order_details,order_id):
#     logging.info("Starting form open process")
    
#     target_address = clean_address(order_details)
#     form_types = [
#         'Interior BPO - W Rentals', 'Exterior Enhanced BPO', 'Interior BPO', 'Exterior BPO',
#         'Exterior BPO - W Rentals', '5 Day MIT ARBPO', '5 Day Interior Appraiser Reconciled BPO',
#         '5 Day Exterior Appraiser Reconciled BPO', '5 Day Exterior BPO - W Rentals',
#         '5 Day Exterior BPO', '5 Day Interior BPO', '5 Day Interior BPO - W Rentals',
#         "3 Day Exterior BPO - W Rentals"
#     ]

#     if not orders:
#         logging.info("No orders in portal")
#         return

#     address_list = []
#     matched, order, status = find_matching_order(orders, target_address, form_types,order_id)

#     if matched:
#         if status == "matched":
#             order_url = f"https://valuationops.homegenius.com/VendorPortal/EditReport?ItemId={order['ItemId']}&EntityType=Vendor"
#             logging.info("Form matched. Opening in browser.")
#             redbell_launch_browser_and_open_form(order_url, session)
#             return
#         else:
#             logging.info(f"Form type mismatch: {order['ProductDesc']}")
#             return
#     else:
#         for order in orders:
#             address_list.append(order['PropAddress'])

#         # ai_matched_order = try_ai_address_match(address_list, target_address, orders, form_types, order_details)
#         # if ai_matched_order:
#         #     order_url = f"https://valuationops.homegenius.com/VendorPortal/EditReport?ItemId={ai_matched_order['ItemId']}&EntityType=Vendor"
#         #     launch_browser_and_open_form(order_url, session)

def redbell_formopen_fill(orders, driver,session, merged_json, order_details,order_id):
    logging.info("Starting form open process")

    target_address = clean_address(order_details)

    form_types = [
        'Interior BPO - W Rentals', 'Exterior Enhanced BPO', 'Interior BPO', 'Exterior BPO',
        'Exterior BPO - W Rentals', '5 Day MIT ARBPO', '5 Day Interior Appraiser Reconciled BPO',
        '5 Day Exterior Appraiser Reconciled BPO', '5 Day Exterior BPO - W Rentals',
        '5 Day Exterior BPO', '5 Day Interior BPO', '5 Day Interior BPO - W Rentals',
        "3 Day Exterior BPO - W Rentals"
    ]

    if not orders:
        logging.info("No orders in portal")
        return

    address_list = []
    matched, order, status = find_matching_order(orders, target_address, form_types, order_id)

    if matched:
        if status == "matched":
            order_url = f"https://valuationops.homegenius.com/VendorPortal/EditReport?ItemId={order['ItemId']}&EntityType=Vendor"
            logging.info("Form matched. Opening in browser.")
            redbell_launch_browser_and_open_form(order_url, session)  # Uses same session
            return
        else:
            logging.info(f"Form type mismatch: {order['ProductDesc']}")
            return
    else:
        for order in orders:
            address_list.append(order['PropAddress'])

        logging.info(f"No exact address match found. Address list: {address_list}")
        # Optional: you can handle AI matching here
        # ai_matched_order = try_ai_address_match(address_list, target_address, orders, form_types, order_details)
        # if ai_matched_order:
        #     order_url = f"https://valuationops.homegenius.com/VendorPortal/EditReport?ItemId={ai_matched_order['ItemId']}&EntityType=Vendor"
        #     redbell_launch_browser_and_open_form(order_url, session)