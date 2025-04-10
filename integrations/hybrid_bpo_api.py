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
     
        # {
        #     "order_id": 9,
        #     "client_name": "Karen",
        #     "main_client": "Karen",
        #     "portal_name": "RedBell",
        #     "portal_id": 12,
        #     "portal_url": "https://valuationops.homegenius.com/VendorPortal",
        #     "username": "reokarenfolgheraiter@gmail.com",
        #     "password": "$K@ren!!247",
        #     "session": "59167B58E93F25E72A0424EB7BDCBB9F3C4DA746DD609AD72C6CD4EE5EC3EF2A87D69148F1EDD7F89EC75401B78AC3F0B3C2B833E13955B03655825584A4F7E435C055FBD52B566D0A0571B3E606AA9D30688335CD6486ACC05634CC7DCF9C305F35534A61BD5C90FBDAE1D5CAC82A1AC75C424D3FC9746DC94E2072B20918CA9095E33677F417CABE3FC20E3A77A4853E79C364BD3278F47E3A939966C9C03CB9C809FE2C6C612A11959545A9952960FFC3160B528FBB94E7666A9F79B43720A795616683C76508F000BBAC1036D09C887175A003288DB1B5CD4EF5E23CCD82AB3EBD79578A2A81FE52161E48495CE93560ACB331DC262A188F312FCC44D63C589764F6287C72400B50C4D1F8E22A6FC980B8C27ED814EBF299E4BDDC584ECA7CBA745BC6520CCE4E779D8B7241D3DC916179B355FDBB39C760331CCE5661FEAD7DFC7EB1CB9762A7714CA9384372371F221028698376F5BCD5A056C237E74A44F46E64",
        #     "proxy": "",
        #     "account_status": "Active"
        # },
        {
            "order_id": 10,
            "client_name": "Keystone Holdings",
            "main_client": "KSH_AudreyWilliams",
            "portal_name": "Proteck",
            "portal_id": 12,
            "portal_url": "https://www.protk.com/net/Entry.aspx",
            "username": "Audrey63",
            "password": "0cg3hyKq",
            "session": "",
            "proxy": "",
            "account_status": "Active"
        }
        ]
        return order_details

    