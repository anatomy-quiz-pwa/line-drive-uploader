import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# 檢查必要的環境變數
assert GOOGLE_SERVICE_ACCOUNT_JSON, "Missing GOOGLE_SERVICE_ACCOUNT_JSON"
assert LINE_CHANNEL_ACCESS_TOKEN, "Missing LINE_CHANNEL_ACCESS_TOKEN"
assert LINE_CHANNEL_SECRET, "Missing LINE_CHANNEL_SECRET"

# 可選的 Shared Drive ID
SHARED_DRIVE_ID = os.getenv("SHARED_DRIVE_ID")  # 可留空；設了就會強制使用這顆 Shared Drive

# 可選的上傳資料夾名稱
UPLOAD_FOLDER_NAME = os.getenv("UPLOAD_FOLDER_NAME", "LINE Bot 檔案上傳")  # 預設值 