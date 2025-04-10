import re
import logging
from ssl import Options
import webbrowser

from utils.helper import clean_address,get_order_address_from_assigned_order  # For opening the form link
import re
import logging
from utils.helper import clean_address, get_order_address_from_assigned_order  # For opening the form link

def find_matching_order(orders, target_address, form_types, order_id):
    order = get_order_address_from_assigned_order(order_id)
    order_address = clean_address(order)
    
    # Iterate through each order
    for order in orders:
        # order['PropAddress'] = order['PropAddress'].replace(",", "")
        # cleaned_text1 = re.sub(r'[\"\'\-,:/]', '', order['PropAddress'])
        # cleaned_text = re.sub(r'\s+', '', cleaned_text1)
        # order['PropAddress'] = cleaned_text.upper()
        order_address_from_portal=clean_address( order['PropAddress'])

        # Address found on portal
        if order_address == order_address_from_portal:
            address_status = True
            print("Address Found {}".format(order['PropAddress']))
            logging.info("Address Found {}".format(order['PropAddress']))
            return True, order, "matched"
        else:
            # If not matched, continue to next iteration
            continue

    # If no match is found
    return False, None, "not_found"

                #Form founded


    #             def find_matching_order(orders, target_address, form_types,order_id):
    # for order in orders:
    #     order=get_order_address_from_assigned_order(order_id)
    #     order_address = clean_address(order)
    #     if order_address == target_address:
    #         if order['ProductDesc'] in form_types:
    #             return True, order, "matched"
    #         else:
    #             return True, order, "wrong_form"
    # return False, None, "not_found"
