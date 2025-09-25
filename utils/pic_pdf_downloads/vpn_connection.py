import requests
import json
import logging

def vpn_checking():
    try:      
            session=requests.session()
            ip_test_url1="https://ipwhois.app/json/"
            ipapify = session.get(ip_test_url1)
            ipapify.raise_for_status()
            ipadress=json.loads(ipapify.text)['ip']
            country=json.loads(ipapify.text)['country']
            print(ipadress)
            print(country)

            # Check if the country is not the US
            if country == "United States":
                print("System IP is US-based.")
                logging.info("System IP is US-based.")
                return True
            else: 
                print("VPN not connected or IP address is not in the US.")
                logging.info("VPN not connected or IP address is not in the US.")
                return False
    except requests.exceptions.HTTPError as e:
            print(f"HTTP error occurred: {e}")     
            logging.error(f"HTTP error occurred: {e}")   
            return False