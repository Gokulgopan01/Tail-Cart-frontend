from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.pic_pdf_downloads.pdf_downloader import pdf_downloader
from utils.pic_pdf_downloads.image_downloader import download_image


class Gamls:

    def process_mls_actions(self,order_data):
        try:

            mlslogin,driver=self.mls_login(order_data)
            print("GAMLS login Function called")
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
                print(f"failed_list : {failed_list}")
            else:
                print('login failed. Status changed')  
                driver.quit()
        except Exception as e:           
            print(f"Error in the program: {e}")        

    def mls_login(self,order_data):

        try:
            print(order_data['Username'])
            print(order_data['Password'])
            # options=Options()
            # options.add_argument(f"--proxy-server={order['proxy']}")
            #---------------------#
            driver = webdriver.Chrome()
            driver.get("https://www.gamls.com/")
            WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.NAME, "username"))).send_keys(order_data['Username'])
            WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.NAME, "password"))).send_keys(order_data['Password'])
            WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="button-gamls-login"]'))).click()
            login_check=WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success")))

            if 'successfully logged in' in login_check.text:
                return True,driver
            else:
                return False,driver

        except Exception as e:
            print(f"Error in the program, login failed: {e}")


    def comp_search(self,driver,comp_name,mls_id,filepath):

        try:

            status={'pic':False,'pdf':False}
            print("comp search started")
            driver.get(f"https://members.gamls.com/search/propertydetail/listingID/{mls_id}/oom/0")
            time.sleep(5)
            records=driver.find_elements(By.XPATH, '//div[@class="col" and contains(text(), "Listing Not Found.")]')
            

            if len(records)==0:

                print("Comparable found successfull")
                try:
                    val= pdf_downloader(driver,comp_name,filepath)
                    status['pdf']=val
                except Exception as e:
                    print("PDF download failed")    
                try:
                    img_element = driver.find_element(By.XPATH, "//a[@data-lightbox='listing-set']")
                    if img_element:
                        img_src_url = img_element.get_attribute("href")
                        val=download_image(img_src_url,comp_name,filepath)
                        status['pic']=val
                        print("Image download sucessfull")
                        
                    else:
                        print("Image not found") 
                        

                except Exception as e:
                    print("No image found")
                
                print("pdf download sucessfull")
                return status
            else:
                print("No comparable found") 
                return status 

        except Exception as e:
            print(f"Error in the program: {e}")
                
    

    