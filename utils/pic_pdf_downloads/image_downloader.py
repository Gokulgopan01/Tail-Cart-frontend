import os
import requests

def download_image(url,comp_name,path):
        try:
            response = requests.get(url)
            if not os.path.exists(path):
                os.makedirs(path)
            filepath = os.path.join(path, f"{comp_name}.png")
            with open(filepath,'wb') as file:
                file.write(response.content)
            return True  
        except Exception as e:
            print("Exception in download_image: ", e)
            return False