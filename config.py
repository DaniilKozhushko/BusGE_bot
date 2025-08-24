import os
from dotenv import load_dotenv

# loading environment variables
load_dotenv()

# assigning values to their variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TTC_BUS_API = os.getenv("TTC_BUS_API")
BASE_TBILISI_URL = os.getenv(f"BASE_TBILISI_URL")
BASE_BATUMI_URL = os.getenv(f"BASE_BATUMI_URL")
ADMIN = os.getenv("ADMIN")