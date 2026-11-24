# config.py
import os

STATE_FILE = "state.json"
LOGIN_URL  = "https://www-daily.yuntim.com/bizmodule/bteamLogin/login.htm"

# 有头/无头：本地默认有头，CI 传 HEADLESS=true 即无头
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"