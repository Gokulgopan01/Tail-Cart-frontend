import os
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
exe_path = desktop_path + r"\main.exe"
# API Endpoints
BASE_URL = "http://192.168.2.51:8000/hybrid/api/v1/autologin"
LOGIN_API = "http://192.168.2.51:8000/hybrid/api/v1/auth/signin"
ASSIGNEDORDERS_URL="http://192.168.2.51:8000/hybrid/api/v1/assigned_orders/"

AUTHENTICATOR_API_URL="https://us-central1-crack-mariner-131508.cloudfunctions.net/Ecesis-Authpp"
API_HEADERS_CONTENT_TYPE="application/json"
CREDENTIALS_URL = "http://192.168.2.51:8000/hybrid/api/v1/entry/entry-client-account/"
PIC_PDF_UPLOAD_URL = "http://192.168.2.51:8000/hybrid/api/v1/pic_pdf_downloader/get-comp-path/"
BASE_URL_ENTRY = "https://valuationops.homegenius.com/VendorBpoForm"
RESEARCHPAD_DATA_URL='http://192.168.2.51:8001/api/v1/entry-data/'
STATUS_UPDATE_URL = "http://192.168.2.51:8000/hybrid/api/v1/status_update/products"
ACCOUNT_INACTIVE="http://192.168.2.51:8000/hybrid/api/v1/client/client-account-status/"
VERSION_FILE = "1.4"
MAIN_EXE = exe_path
REMOTE_VERSION_URL = "http://192.168.2.51:8000/hybrid/api/v1/autologin/autologin-version"
VIEW_FILE_BASE_URL = "http://192.168.2.51:8005/view_file?file_path="
FILE_SERVER_URL = "http://192.168.2.51:8005/files/view_file?file_path="
