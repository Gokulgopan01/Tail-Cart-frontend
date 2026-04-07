# API Endpoints

import os
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
exe_path = desktop_path + r"\main.exe"
BASE_URL = "http://192.168.2.51:8000/hybrid/api/v1/autologin"
LOGIN_API = "http://192.168.2.51:8000/hybrid/api/v1/auth/signin"
ASSIGNEDORDERS_URL="http://192.168.2.51:8000/hybrid/api/v1/assigned_orders/"
#AUTHENTICATOR_API_URL="https://us-central1-crack-mariner-131508.cloudfunctions.net/Ecesis-Authpp"
AUTHENTICATOR_API_URL="http://authenticator.ecesistech.com/"
API_HEADERS_CONTENT_TYPE="application/json"
CREDENTIALS_URL = "http://192.168.2.51:8000/hybrid/api/v1/entry/entry-client-account/"
PIC_PDF_UPLOAD_URL = "http://192.168.2.51:8000/hybrid/api/v1/pic_pdf_downloader/get-comp-path/"
BASE_URL_ENTRY = "https://valuationops.homegenius.com/VendorBpoForm"
RESEARCHPAD_DATA_URL='http://192.168.2.51:8001/api/v1/entry-data/'
STATUS_UPDATE_URL = "http://192.168.2.51:8000/hybrid/api/v1/status_update/"
ACCOUNT_INACTIVE="http://192.168.2.51:8000/hybrid/api/v1/client/client-account-status/"
VERSION_FILE = "2.6"
MAIN_EXE = exe_path
REMOTE_VERSION_URL = "http://192.168.2.51:8000/hybrid/api/v1/autologin/autologin-version"
PORTAL_LOGIN_CONFIRMATION="http://192.168.2.51:8000/hybrid/api/v1/autologin/update-autologin-check?order_id="
tfs_statuschange_url = "http://tfs-sandbox.ecesistech.com/autobpo_test/Home/ProcUpdateTFSstatusEntry"
bpo_statuschange_url = "http://tfs-sandbox.ecesistech.com/autobpo_test/Home/ProcUpdateAutoEntry"

RABBIT_URL = "amqp://glogger:123@192.168.2.41/"
QUEUE_NAME = "autologin-tool"


# import os
# desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
# exe_path = desktop_path + r"\main.exe"
# BASE_URL = "https://api.hybridbpo.ecesistech.com/hybrid/api/v1/autologin"
# LOGIN_API = "https://api.hybridbpo.ecesistech.com/hybrid/api/v1/auth/signin"
# ASSIGNEDORDERS_URL="https://api.hybridbpo.ecesistech.com/hybrid/api/v1/assigned_orders/"
# #AUTHENTICATOR_API_URL="https://us-central1-crack-mariner-131508.cloudfunctions.net/Ecesis-Authpp"
# AUTHENTICATOR_API_URL="http://authenticator.ecesistech.com/"
# API_HEADERS_CONTENT_TYPE="application/json"
# CREDENTIALS_URL = "https://api.hybridbpo.ecesistech.com/hybrid/api/v1/entry/entry-client-account/"
# PIC_PDF_UPLOAD_URL = "https://api.hybridbpo.ecesistech.com/hybrid/api/v1/pic_pdf_downloader/get-comp-path/"
# BASE_URL_ENTRY = "https://valuationops.homegenius.com/VendorBpoForm"
# VERSION_FILE = "1.7"
# MAIN_EXE = exe_path
# REMOTE_VERSION_URL = "https://api.hybridbpo.ecesistech.com/hybrid/api/v1/autologin/autologin-version"
# PORTAL_LOGIN_CONFIRMATION="https://api.hybridbpo.ecesistech.com/hybrid/api/v1/autologin/update-autologin-check?order_id="
# tfs_statuschange_url = "https://bpotrackers.com/bvupcqp/home/ProcUpdateTFSstatusEntry"
# bpo_statuschange_url = "https://bpotrackers.com/bvupcqp/Home/ProcUpdateAutoEntry"

# RABBIT_URL = "amqp://guest:guest@api.hybridbpo-msgbroker.ecesistech.com:5672/"
# QUEUE_NAME = "autologin-tool"
# RESEARCHPAD_DATA_URL='https://api.hybridbpo-rpad.ecesistech.com/api/v1/entry-data/'
# STATUS_UPDATE_URL = "https://api.hybridbpo.ecesistech.com/hybrid/api/v1/status_update/"
# ACCOUNT_INACTIVE="https://api.hybridbpo.ecesistech.com/hybrid/api/v1/client/client-account-status/"







