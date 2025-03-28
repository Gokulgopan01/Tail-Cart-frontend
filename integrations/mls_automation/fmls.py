from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Keys
from utils.pic_pdf_downloads.pdf_downloader import pdf_downloader
from utils.pic_pdf_downloads.image_downloader import download_image

class Fmls:

    def process_mls_actions(self,order_data):
        try:
            print("FMLS login Function called")
            mlslogin,driver=self.mls_login(order_data)
            print("FMLS login Function called")
            if mlslogin:
                print("Login successful,Proceed searching the comparable")
                failed_list=[]
                for comp_name, mls_id in order_data["mls_id"].items():
                    print(comp_name, mls_id)
                    filepath=order_data["Path"]
                    comp_process_status=self.comp_search(driver,comp_name,mls_id,filepath) 
                    print(f"comp download status of {comp_name} : {comp_process_status} ")
                    if comp_process_status['pdf']==False:
                        failed_list.append(f"{comp_name} pdf")
                    if comp_process_status['pic']==False:
                        failed_list.append(f"{comp_name} pic")
                driver.quit()  
                failed_list=', '.join(failed_list)
                print(f"failed_list : {failed_list}")
                return failed_list
            else:
                print('login failed. Status changed')  
                driver.quit()
        except Exception as e:           
            print(f"Error in the program: {e}")      


    def mls_login(self,order_data):
        try:
            # options=Options()
            # options.add_argument(f"--proxy-server={order['proxy']}")
            driver = webdriver.Chrome()
            driver.get("https://matrix.fmlsd.mlsmatrix.com/")
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.NAME, "loginId"))).send_keys(order_data['Username'])
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.NAME, "password"))).send_keys(order_data['Password'])
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="btn-login"]'))).click()
            time.sleep(5)
            current_url = driver.current_url
            print(current_url)

            if "Default.aspx" in current_url:
                return "Login successful",driver
            else:
                return "Login failed",driver
        
        except Exception as e:
            print(f"Error in the program: {e}")

    def comp_search(self,driver,comp_name,mls_id,filepath):
        try:
            status={'pic':False,'pdf':False}
            print("comp search started")
            driver.get('https://matrix.fmlsd.mlsmatrix.com/Matrix/Default.aspx')
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='ctl02_m_ucSpeedBar_m_tbSpeedBar']"))).send_keys(mls_id)
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='ctl02_m_ucSpeedBar_m_tbSpeedBar']"))).send_keys(Keys.RETURN) 
            time.sleep(5)
            mls_search = driver.find_elements(By.XPATH, '//a[@data-mtx-track="Results - In-Display Full Link Click"]')

            if len(mls_search)!=0:
                WebDriverWait(driver, 70).until(EC.element_to_be_clickable((By.XPATH, '//a[@data-mtx-track="Results - In-Display Full Link Click"]'))).click()
                try:
                    element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "d27m28"))
                    )
                    # Modify the text inside the element
                    driver.execute_script("arguments[0].innerText = '';", element)
                    val=pdf_downloader(driver,comp_name,filepath)
                    status['pdf']=val
                except Exception as e:
                    print("PDF download failed") 

                try:
                    img_element = driver.find_element(By.XPATH,"//td[@class='imageRow']/img")

                    if img_element:
                        img_src_url = img_element.get_attribute("src")
                        val=download_image(img_src_url,comp_name,filepath)
                        status['pic']=val
                        print("Image download sucessfull")                   
                    else:
                        print("Image not found")
            
                except Exception as e:
                    print("No image found")

                return status
            else:
                print("No comparable found")
                return status 

        except Exception as e:
            print(f"Error in the program: {e}")        