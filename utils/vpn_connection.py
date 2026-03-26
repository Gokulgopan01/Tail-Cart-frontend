import requests
import json
import logging

def vpn_checking():
    try:
        session = requests.Session()

        # Step 1: Get the client IP
        ip_url = "http://authenticator.ecesistech.com/authenticate-ip"
        ip_response = session.get(ip_url, timeout=10)
        ip_response.raise_for_status()
        data = ip_response.json()
        client_ip = data.get("client_ip")

        print(f"Client IP: {client_ip}")
        logging.info(f"Client IP: {client_ip}")

        if not client_ip:
            logging.error("Failed to fetch client IP.")
            return False

        # Step 2: Fetch allowed IPs
        allowed_url = "https://bpoacceptor.com/allowed_ips.txt"
        allowed_response = session.get(allowed_url, timeout=10)
        allowed_response.raise_for_status()

        allowed_ips = set(
            line.strip() for line in allowed_response.text.splitlines() if line.strip()
        )

        # Step 3: Check if IP is allowed
        if client_ip in allowed_ips:
            print(" IP is allowed. VPN is connected properly.")
            logging.info("IP is allowed. VPN connection verified.")
            return True
        else:
            print(" IP is NOT in the allowed list. VPN might be off.")
            logging.warning("IP not in allowed list. VPN might not be active.")
            return False

    except requests.exceptions.RequestException as e:
        print(f"HTTP error occurred: {e}")
        logging.error(f"HTTP error occurred: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        logging.error(f"JSON parsing error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        logging.error(f"Unexpected error: {e}")
        return False
