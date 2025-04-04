import re
import logging
from ssl import Options
import webbrowser  # For opening the form link

# Set up basic logging configuration
logging.basicConfig(level=logging.INFO)

def open_matching_form(Address_tobe_checked, orders):
    print('==============================')
    options = Options()

    
    faddress =Address_tobe_checked.replace(",", "")
    addressfromtfs = re.sub(r'[\"\'\-,:/]', '', faddress)
    cleaned_text = re.sub(r'\s+', '', addressfromtfs)
    address = cleaned_text.upper()
    
    logging.info("Subject address after merging: {}".format(address))

    form_type = [
        'Interior BPO - W Rentals', 'Exterior Enhanced BPO', 'Interior BPO', 'Exterior BPO',
        'Exterior BPO - W Rentals', '5 Day MIT ARBPO', '5 Day Interior Appraiser Reconciled BPO',
        '5 Day Exterior Appraiser Reconciled BPO', '5 Day Exterior BPO - W Rentals', '5 Day Exterior BPO',
        '5 Day Interior BPO', '5 Day Interior BPO - W Rentals', "3 Day Exterior BPO - W Rentals"
    ]
    
    print('Refreshing Portal')

    orderurl = ''
    address_list = []
    address_status = False
    newform = 0

    if len(orders) > 0:
        # Finding address from portal
        for order in orders:
            order['PropAddress'] = order['PropAddress'].replace(",", "")
            cleaned_text1 = re.sub(r'[\"\'\-,:/]', '', order['PropAddress'])
            cleaned_text = re.sub(r'\s+', '', cleaned_text1)
            order['PropAddress'] = cleaned_text.upper()

            # Address found on portal
            if address == order['PropAddress']:
                address_status = True
                print("Address Found {}".format(order['PropAddress']))
                logging.info("Address Found {}".format(order['PropAddress']))

                # Form found
                if order['ProductDesc'] in form_type:
                    print("Form matched")
                    print(order['OrderId'], order['ItemId'])
                    print(f"https://valuationops.homegenius.com/VendorPortal/EditReport?ItemId={order['ItemId']}&EntityType=Vendor")
                    orderurl = f"https://valuationops.homegenius.com/VendorPortal/EditReport?ItemId={order['ItemId']}&EntityType=Vendor"
                    logging.info("Form Matched")
                    break
                # Not doing form
                else:
                    print("Form not matched---New Type")
                    logging.info(f"Form not Found --New Type {order['ProductDesc']}")
            # Address not Found on portal
            else:
                print(f"Address Not Found {order['PropAddress']}")
                logging.info(f"Address Not Found {order['PropAddress']}")
                address_list.append(cleaned_text1)