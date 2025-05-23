import os
from dotenv import load_dotenv
import requests
from config import env
# Load environment variables from a .env file
load_dotenv()

# Retrieve the API key from the environment variables
API_KEY = os.getenv('API_KEY')
USER_CREDENTIALS_URL = env.CREDENTIALS_URL 

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



    def get_entry_order():
        """Returns the order details as a dictionary."""
        try:
            order_id=50
            response = requests.get(f"{USER_CREDENTIALS_URL}{order_id}")
            response.raise_for_status()  # Raises exception for HTTP error codes
            json_data = response.json()

            if (
                isinstance(json_data, dict)
                and json_data.get("status_code") == 200
                and isinstance(json_data.get("content"), dict)
                and isinstance(json_data["content"].get("data"), (dict, list))
            ):
                data = json_data["content"]["data"]
                print("Successfully retrieved data:")

                # Wrap in list if it's a single dict
                if isinstance(data, dict):
                    orders = [data]
                else:
                    orders = data

                for order in orders:
                    print(order)

                return orders

            else:
                print("Invalid structure or missing fields in response.")
                # Debug info
                print(f"status_code: {json_data.get('status_code') if isinstance(json_data, dict) else 'N/A'}")
                print(f"content present: {'content' in json_data if isinstance(json_data, dict) else 'N/A'}")
                if isinstance(json_data, dict) and "content" in json_data:
                    print(f"data type: {type(json_data['content'].get('data'))}")
                return None

                
        except requests.RequestException as e:
            print(f" Request error: {e}")
            return None
        except ValueError:
            print(" Response was not valid JSON.")
            return None


        
        order_details = [
     
        # {
        #     "order_id": 58,
        #     "client_name": "Ecesis",
        #     "main_client": "Roselyn",
        #     "portal_name": "RedBell",
        #     "portal_id": 2,
        #     "portal_url": "https://valuationops.homegenius.com/VendorPortal",
        #     "username": "silvercirclebpos@gmail.com",
        #     "password": "Re@2025bpo",
        #     "session": "6A3CBEDB74088199B26921AF230D081C45D58C0897DC6399CE109593757393A83C73DA4C3E9604D609C97A7F002AEE2A610FE469B9B6D932CB6522BB8EDD56DEF597713E2EF71B4927D828AD837CE62B97E8DE4FB48CFED263A54B2814C742B9444DF8273EC3C587DA231DA82250A83D24AD471BA98BE8EAE214B0D05CAA58CC523E8C92E12E82CBEE5230993B69083A1C802D43C78702073D7AB5DD41172EC844930A7FC36AFE027B6308E1628F811C56A72D595F08414F0A50E9C6ACFC27C4F5454405934B717E99228FD34CC69B7C6161697741B2A8DC094F8BF3846D75543AF4F9FBC04CE77FECC5F6881B98194797A8C3EA01E8C60457FF914156300C57C60DE70D8955ECA4E18DC2DBF013AAA2406439D5843BC4710F890531A485FD2984CA83778D7C6F65DD259CAA2A342F56427E4D3E469C8119253521578C93910A10A38EC317937B5B8740B214F318641B4C200C7ACAA8D8CEE14A3E2822F89FC9B2159132",
        #     "__RequestVerificationToken": "SDaZfMfKH9Q8hyTeQqiBBG5A7QMWUY7hoGRDqE4-BPdvj-av_RU7zouQLnzn9hPffTIym27e-E1UflrTGVEoTzl0KX81",
        #     "proxy": "",
        #     "account_status": "Active"
        # }


             
        {
            "order_id": 58,
            "client_name": "Bang",
            "main_client": "Betty Spradley",
            "portal_name": "RedBell",
            "portal_id": 2,
            "portal_url": "https://valuationops.homegenius.com/VendorPortal",
            "username": "memphisbpo@bangrealty.com",
            "password": "Louisespra127$0$",
            "session": "D66BA2D5A397DFD02FE53403DE4D9C1FAC2D8E3D35D47F8BBDFB010F32CEAD2B2370D0D1108F698847701A5AECB1D155B98E1ADD3DFCF1F5A05881A98F15E6AD56802E6BA518009D805498E84C5F6D2F473EA34F0A6BCD39CFF2253DD32ED66724DFBF30325F8C7660AFF10500029AE4EBE571841745741AE5B5032B745647B34772F63B8E3CF5D559FABD78D00587C1303008F3200E342073DB2F2C268025159D439FA217E055A71B648E4B25704FBF6B4BFD584DDB92E3B0DDB180D892E6AACF825BAF311A6FAA67E5533DA4FFC527A4E405EC99D425A7E23A6B96EE09FA845C540846CB962A48D7C1E49F3B28F06380138E2B9BB069782B49FD4870766BB7C747D7054E74BC5C1CC2C69F3506C1FB247FDA41C428B80567958EF6DCF162094EA06F5A52F10A945E248B64E256AB09F650FF02589D36F01A70753D482CD8DD9B2EAEC9DCF04D05F44F288CF50873C76FB94E82",
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

    