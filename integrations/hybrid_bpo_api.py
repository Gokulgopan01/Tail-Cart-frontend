from json import JSONDecodeError
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



    # def get_entry_order(order_id):
    #     """Returns the order details as a dictionary."""
    #     try:
    #         #order_id=110
    #         response = requests.get(f"{USER_CREDENTIALS_URL}{order_id}")
    #         response.raise_for_status()  # Raises exception for HTTP error codes
    #         json_data = response.json()

    #         if (
    #             isinstance(json_data, dict)
    #             and json_data.get("status_code") == 200
    #             and isinstance(json_data.get("content"), dict)
    #             and isinstance(json_data["content"].get("data"), (dict, list))
    #         ):
    #             data = json_data["content"]["data"]
    #             print("Successfully retrieved data:")

    #             # Wrap in list if it's a single dict
    #             if isinstance(data, dict):
    #                 orders = [data]
    #             else:
    #                 orders = data

    #             for order in orders:
    #                 print(order)

    #             return orders

    #         else:
    #             print("Invalid structure or missing fields in response.")
    #             # Debug info
    #             print(f"status_code: {json_data.get('status_code') if isinstance(json_data, dict) else 'N/A'}")
    #             print(f"content present: {'content' in json_data if isinstance(json_data, dict) else 'N/A'}")
    #             if isinstance(json_data, dict) and "content" in json_data:
    #                 print(f"data type: {type(json_data['content'].get('data'))}")
    #             return None

                
    #     except requests.RequestException as e:
    #         print(f" Request error: {e}")
    #         return None
    #     except ValueError:
    #         print(" Response was not valid JSON.")
    #         return None
    def get_entry_order(order_id):
        """Fetch and return order details as a list of dictionaries."""
        #order_id=145
        try:
            response = requests.get(f"{USER_CREDENTIALS_URL}{order_id}", timeout=5)
            response.raise_for_status()  # Raise an error for bad HTTP status codes

            # Protect against empty or non-JSON responses
            if not response.text.strip():
                print(" Empty response received from server.")
                return None

            try:
                json_data = response.json()
            except JSONDecodeError:
                print("Invalid JSON in response.")
                print("Raw response text:", response.text)
                return None

            # Validate structure
            if (
                isinstance(json_data, dict)
                and json_data.get("status_code") == 200
                and isinstance(json_data.get("content"), dict)
                and isinstance(json_data["content"].get("data"), (dict, list))
            ):
                data = json_data["content"]["data"]
                orders = [data] if isinstance(data, dict) else data

                print("Successfully retrieved order data:")
                for order in orders:
                    print(order)

                return orders

            else:
                print(" Invalid response structure or missing expected fields.")
                print(f"  status_code: {json_data.get('status_code')}")
                print(f"  'content' in response: {'content' in json_data}")
                print(f"  'data' type: {type(json_data.get('content', {}).get('data'))}")
                return None

        except requests.RequestException as e:
            print(f"🔌 Request error: {e}")
            return None

        
        

        