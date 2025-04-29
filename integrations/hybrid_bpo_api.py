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
        order_details = [
     
        {
            "order_id": 10,
            "client_name": "Keystone Holdings",
            "main_client": "KSH_GeoffFolkerth",
            "portal_name": "RedBell",
            "portal_id": 12,
            "portal_url": "https://valuationops.homegenius.com/VendorPortal",
            "username": "geoffre858@gmail.com",
            "password": "SwapMeet13!",
            "session": "C4FC68CEA860BE729DF164B6C8C8B94C6EE694D9F4A3B5CAD167CCE1400DC2AD8EDF96D50BBA6A41A6FE31A81D098A1FDD98A32485E30008716E3AD5ECFDC9C1E34A0FE7D2F34C43FEC8E37F1675F454BFA3F97EC8A622F70F6A23FE16D7F49A2192200B31C1EDC8FB1EDE77BECCB49218F4FE8F63B15272E3DB5C9F7CB3EF98AE35ED2C80910C68AAED5C25E5230ED8F87372BA987ED4B90DA24840C3B716344CB2FD0C6C913429D2014594C64A9EB4020EE55D73C1FCF8A88FC48B00975F3EBEAC0A7F17775886F8390F8D542B8FAD8115751E9614ABF9A84AD741F33866E92A38368EB3A075A74868D40B745EA7B4A8A13ECB9AF231E116C30C12E4F5A630091B4F53E4B2C13E5CAAB20530317B6E36C4E70784420F64AACFD6E3E00BCF1F9DCD9FE76C00122AF041752644266FD5B6ED77E61D2490E2506AFBEB1ACCFF8A79477F5F7253E3031C9903BBED66BE31EEA4E97F",
        "__RequestVerificationToken": "SDaZfMfKH9Q8hyTeQqiBBG5A7QMWUY7hoGRDqE4-BPdvj-av_RU7zouQLnzn9hPffTIym27e-E1UflrTGVEoTzl0KX81",
            "proxy": "",
            "account_status": "Active"
        }
        # {
        #     "order_id": 10,
        #     "client_name": "Keystone Holdings",
        #     "main_client": "KSH_AudreyWilliams",
        #     "portal_name": "Proteck",
        #     "portal_id": 12,
        #     "portal_url": "https://www.protk.com/net/Entry.aspx",
        #     "username": "Audrey63",
        #     "password": "0cg3hyKq",
        #     "session": "",
        #     "proxy": "",
        #     "account_status": "Active"
        # }
        ]
        return order_details

    