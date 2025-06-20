# import json
# import os

import json
import os


# login_data_file = "login_data.json"

# def save_login_data(logged_in, token,user_details):
#     data = {
#         "logged_in": logged_in,
#         "user_details": user_details,
#         "token": token
#     }
#     with open(login_data_file, "w") as file:
#         json.dump(data, file)

# # def load_login_data():
# #     if os.path.exists(login_data_file):
# #         with open(login_data_file, "r") as file:
# #             data = json.load(file)
# #             return {
# #                 "logged_in": data.get("logged_in", False),
# #                 "token": data.get("token"),
# #                 "user_details": data.get("user_details")
# #             }
# #     return {
# #         "logged_in": False,
# #         "token": None,
# #         "user_details": None
# #     }
# import os
# import json

# login_data_file = "login_data.json"  # ensure this variable is defined at the top

# def load_login_data():
#     if os.path.exists(login_data_file):
#         try:
#             with open(login_data_file, "r") as file:
#                 content = file.read().strip()

#                 if not content:
#                     raise ValueError("File is empty")

#                 data = json.loads(content)
#                 return {
#                     "logged_in": data.get("logged_in", False),
#                     "token": data.get("token"),
#                     "user_details": data.get("user_details")
#                 }
#         except (json.JSONDecodeError, ValueError):
#             print("⚠️ Warning: login_data.json is empty or corrupted.")
#             return {
#                 "logged_in": False,
#                 "token": None,
#                 "user_details": None
#             }

#     return {
#         "logged_in": False,
#         "token": None,
#         "user_details": None
#     }


# def logout():
#     if os.path.exists(login_data_file):
#         with open(login_data_file, "w") as file:
#             json.dump({}, file)

# #######################
import os
import json

# ✅ Save in a guaranteed writable directory (APPDATA or fallback to home)
app_data_dir = os.path.join(os.getenv("APPDATA") or os.path.expanduser("~"), "HybridBPO")
os.makedirs(app_data_dir, exist_ok=True)

login_data_file = os.path.join(app_data_dir, "login_data.json")


def save_login_data(logged_in, token, user_details):
    data = {
        "logged_in": logged_in,
        "token": token,
        "user_details": user_details
    }
    try:
        with open(login_data_file, "w") as file:
            json.dump(data, file, indent=2)
        print(f"✅ Login data saved to {login_data_file}")
    except PermissionError as e:
        print(f"❌ Permission denied: {e}")
    except Exception as e:
        print(f"❌ Failed to write login data: {e}")


def load_login_data():
    if os.path.exists(login_data_file):
        try:
            with open(login_data_file, "r") as file:
                content = file.read().strip()
                if not content:
                    raise ValueError("File is empty")
                data = json.loads(content)
                return {
                    "logged_in": data.get("logged_in", False),
                    "token": data.get("token"),
                    "user_details": data.get("user_details")
                }
        except (json.JSONDecodeError, ValueError):
            print("⚠️ Warning: login_data.json is empty or corrupted.")
            return {
                "logged_in": False,
                "token": None,
                "user_details": None
            }
        except Exception as e:
            print(f"❌ Error loading login data: {e}")
            return {
                "logged_in": False,
                "token": None,
                "user_details": None
            }

    return {
        "logged_in": False,
        "token": None,
        "user_details": None
    }


def logout():
    """Clear login data by overwriting with empty JSON."""
    try:
        with open(login_data_file, "w") as file:
            json.dump({}, file)
        print("✅ Login data cleared.")
    except PermissionError as e:
        print(f"❌ Permission denied during logout: {e}")
    except Exception as e:
        print(f"❌ Error during logout: {e}")
