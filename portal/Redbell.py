import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from tkinter import messagebox
import time
from selenium.common.exceptions import TimeoutException, NoSuchElementException
# from utility.helper import log_login_status,initialize_driver
from selenium.webdriver.chrome.service import Service
class PortalLogin:
    def __init__(self, client_data):
        self.client_data = client_data
        self.driver = None  #Store Selenium WebDriver instance
        logging.basicConfig(level=logging.INFO)
    def login(clientData):
        try:
            
            options = Options()
            options.add_argument("--start-maximized")  # Maximize the Chrome window
            options.add_argument("--disable-extensions")  # Disable extensions (optional)
            session=requests.Session()
            if clientData['ip_addr'] !='':
                client_ip=clientData['ip_addr']
                logging.info("Ip address for the corresponding client is:{}".format(client_ip)) 
                options.add_argument('--proxy-server=%s' % client_ip) 
                proxies = {
                    'http': f'http://{client_ip}',
                    'https': f'http://{client_ip}'
                    }
                session.proxies.update(proxies)
                
            else:
                print("Ip address was not found for the corresponding client")
                logging.info("Ip address was not found for the corresponding client") 
            # service = Service(executable_path=r'C:\\chromedriver1.exe')
            # options = webdriver.ChromeOptions()
            # options.add_argument('--headless')
            # options.add_argument('--no-sandbox')
            # options.add_argument('--disable-dev-shm-usage')
            # driver = webdriver.Chrome(service=service, options=options)
            # Check if chromedriver.exe exists at the specified path
            username = clientData['username'].strip()
            login_Data=cursorexec("52","SELECT * FROM redbell WHERE userid='"+username+"'")
            
            chromedriver_path = "C:\\chromedriver.exe"
            if not os.path.isfile(chromedriver_path):
                print("Error: chromedriver.exe not found at the specified path.")
                logging.info("Error: chromedriver.exe not found at the specified path.") 
                exit()


            session,session_Flag=session_check(session,login_Data["Session_cookie"])
            orders=[]
            
            if session_Flag:
                pass
            else:
                login_Flag,session=login_to_portal(login_Data,session)
                if login_Flag:
                    session_Flag=True
                else:
                    session_Flag=False
                    logging.info("Login attempt failed")
                    
            if session_Flag:
                orders,session=fetch_data(session)
                

            else:
                print("Login Error")
                session="Login error"
                
            return orders,session
    
        
        except Exception as e:
            
            logging.info("An error occurred Unbale to login to the portal {}".format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
            logging.info("Login issue in login function") 
            session="Login issue"
            orders="Nothing"#Dummy for orderlist
            return orders,session
        

    def get_headers(additonal_headers):        #Function used to fetch the common headers used for acceptance
        try:
            headers={
                        'authority': 'valuationops.homegenius.com',
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                        'accept-language': 'en-US,en;q=0.5',
                        'referer': 'https://valuationops.homegenius.com/VendorPortal',
                        'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Brave";v="110"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"Windows"',
                        'sec-fetch-dest': 'document',
                        'sec-fetch-mode': 'navigate',
                        'sec-fetch-site': 'same-origin',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/1.0.0.0 Safari/537.36',
                    }
            if len(additonal_headers)> 0 :
                for a_head in additonal_headers: headers[a_head] = additonal_headers[a_head]
            return headers
        except Exception as ex:
            logging.info(ex)

    def session_check(session,session_cookie):
                resp=''
                url = "https://valuationops.homegenius.com/VendorPortalProfileV1"
                if session_cookie != '':
                    data = session_cookie
                    cook ='.ASPXAUTH={};'.format(data)
                    cookie ={'.ASPXAUTH': session_cookie }
                    headers = get_headers({})
                    resp = session.get(url, headers=headers ,cookies=cookie)
                    if 'Profile Information' in resp.text:
                        session.cookies.set('.ASPXAUTH', data)									  
                        session.headers.update(cookie) #session cookie not getting updated after 'get' request
                        logging.info("Session Cookie Active!!!")
                        return session,True
                    else:
                        logging.info("Session Cookie Not Active!!!")
                        return session,False
                else:
                    return session,False

    def login_to_portal(client_data,session):          #Function used to login into the portal
        try:
            url = "https://us-central1-crack-mariner-131508.cloudfunctions.net/Ecesis-Authpp"
            payload = json.dumps({
            "username": client_data['userid']
            })
            headers = {
            'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=payload)

            resp=json.loads(response.text)
            if response.status_code==200:
                cookies=resp['cookies']
                session.cookies.update(cookies)
                
                logging.info("Session from login :{} for the client {}".format(session,client_data['Subclient'])) 
                return True,session
            else:
                logging.info("Server Error with API")
            if response['status']=='failed' and response['cookies']=={}:
                logging.info("Session from login :{} for the client {}".format(session,client_data['Subclient'])) 
                logging.info("LOGIN ERROR")
                return False,session
        except Exception as ex:
            logging.info(ex)

    def fetch_data(session):
        response=session.get("https://valuationops.homegenius.com/VendorPortal/InprogressOrder")
        cookies=session.cookies.get_dict()
        headers = {
        'authority': 'valuationops.homegenius.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://valuationops.homegenius.com',
        'referer': 'https://valuationops.homegenius.com/VendorPortal/InprogressOrder',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
        }
        data = {
            '__aweconid': 'Grid',
            'v': '',
            'orderGenID': '',
            'loanId': '',
            'borrowerName': '',
            'propertyAddress': '',
            'stateAbbr': '',
            'productId': '',
            'orderFromDate': '',
            'orderThruDate': '',
            'orderStatus': '',
            'globalSearch': '',
            'pageSize': [
                '1000',
                '50',
            ],
            'page': '1',
            'tzo': '-330',
        }

        response = requests.post(
            'https://valuationops.homegenius.com/VendorPortal/GetMyOrderItem',
            cookies=cookies,
            headers=headers,
            data=data,
        )
        data=json.loads(response.content)
        orders=data['dt']['it']
        return orders,session

