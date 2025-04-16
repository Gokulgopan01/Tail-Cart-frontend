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
            "session": "E10240DEF95A6563B89F2E5C3447999EEFEC388530F19765A5E23740801A8F9761C2F1EAE0077719825E9E58FBD4BD9E1AC5E7AD22CB2593D36BC86E44BFBCA2ED5466A84FBCA674C89486D9BEB0F2131D570DB51D727B2C0C3BD62D7B5FCB4B1EB7D6B7261DE94C36EF0C893B6AC6C565C7804F8CC622D3A31F3A6930BA7073082221AB596AAE107CD1F53C9439091EF1F5A80E92C5C4759410BBF84B5F672DF5B668048CDDC2CE7A9883A89982F4C900B5729C87436244019F1F92A16A33CC90E20F3C6313BE3FC4815E4E96FF68B83B3D9AE5A9370DB0B3E98A93B59C6A78E08887AA3D87A8A4FC6454842861455FA761259E57A659EF8F5EDAAE54B9383428B0098FB2356F7FF2D8B685F24E42E65C5F7C088C9CBD638A759E2CAA3D977F680F0DAB7D28A8884B08D6EAC665AEB289E2D1B341C5DD6CA3F1B9569088FBEE6CD3254027B058AD06F7A352942D6B808A710706",
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

    