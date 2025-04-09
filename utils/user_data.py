import json
import os

login_data_file = "login_data.json"

def save_login_data(logged_in, token,user_details):
    data = {
        "logged_in": logged_in,
        "user_details": user_details,
        "token": token
    }
    with open(login_data_file, "w") as file:
        json.dump(data, file)

def load_login_data():
    if os.path.exists(login_data_file):
        with open(login_data_file, "r") as file:
            data = json.load(file)
            return {
                "logged_in": data.get("logged_in", False),
                "token": data.get("token"),
                "user_details": data.get("user_details")
            }
    return {
        "logged_in": False,
        "token": None,
        "user_details": None
    }

def logout():
    if os.path.exists(login_data_file):
        with open(login_data_file, "w") as file:
            json.dump({}, file)