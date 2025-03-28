import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Retrieve the API key from the environment variables
API_KEY = os.getenv('API_KEY')


class HybridBPOApi:

    def __init__(self):
        
        self.API_KEY=API_KEY

    

    def loadPortals():

        # api call to load all the portal
        1

    def loadAccounts():
        #api clal to load all the accounts of a user
        1

    def check_application_version():

        return True

    #etc..etc..

    def get_order (self, orderId):
        
        try:
            print("order fetching")
            # api call to get the order details using the order_id
            # order={"orderId":"1010","mls_id":{"a1_mls_id":"20555125824","a2_mls_id":"10380960","a3_mls_id":"8498435","a4_mls_id":"8498436","a5_mls_id":"8498437","a6_mls_id":"8498438"},"Address":"2808 MIRA VISTA LN Rockwall TX 75032","MLS":"GAMLS","Username" :"dawsonlabres","Password":"love", "Path":"S:\\Anisha\\Comparable PIC-PDF Download\\2808 MIRA VISTA LN Rockwall TX 75032"}
            order={"orderId":"1010","mls_id":{"a1_mls_id":"7498101","a2_mls_id":"7498178","a3_mls_id":"7498179","a4_mls_id":"7498180","a5_mls_id":"7498181","a6_mls_id":"7498182"},"Address":"911 Providence Way, Lawrenceville, GA 30046","MLS":"FMLS","Username" :"msreed","Password":"Ledarion#08", "Path":"S:\\Anisha\\Comparable PIC-PDF Download\\911 Providence Way, Lawrenceville, GA 30046"}
            print("Order found")
            return order      
        except Exception as e:
            print(f"Error in the program: {e}")
    def get_entry_order():
        """Returns the order details as a dictionary."""
        order_details = {
            "order_id": 123,
            "client_name": "Roselyn",
            "main_client": "Roselyn",
            "portal_name": "Redbell",
            "portal_id": 12,
            "portal_url":"https://valuationops.homegenius.com/VendorPortal",
            "username": "silvercirclebpos@gmail.com",
            "password": "Re@2025bpo",
            "session": "<><><><>",
            "proxy": "12120",
            "account_status": "Active"
        }
        
        # Return the dictionary directly
        return order_details

    # Example Usage:
    order_dict = get_entry_order()
    print(order_dict)

