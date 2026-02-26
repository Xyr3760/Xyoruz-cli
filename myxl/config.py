import os
from dotenv import load_dotenv

load_dotenv()

BASE_API_URL = os.getenv("BASE_API_URL")
BASE_CIAM_URL = os.getenv("BASE_CIAM_URL")
BASIC_AUTH = os.getenv("BASIC_AUTH")
AX_FP_KEY = os.getenv("AX_FP_KEY")
UA = os.getenv("UA")
API_KEY = os.getenv("API_KEY")
ENCRYPTED_FIELD_KEY = os.getenv("ENCRYPTED_FIELD_KEY")
XDATA_KEY = os.getenv("XDATA_KEY")
AX_API_SIG_KEY = os.getenv("AX_API_SIG_KEY")
X_API_BASE_SECRET = os.getenv("X_API_BASE_SECRET")
CIRCLE_MSISDN_KEY = os.getenv("CIRCLE_MSISDN_KEY")
