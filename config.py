import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# LINE Bot 設定
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "你的 LINE Channel Secret")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "你的 LINE Channel Access Token")

# Google Drive 設定
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON", "你的 Google Service Account 憑證檔案")
UPLOAD_FOLDER_ID = os.getenv("UPLOAD_FOLDER_ID", "Google Drive 的資料夾 ID")

# 應用程式設定
TEMP_FOLDER = "temp_files"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
SUPPORTED_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.mp4', '.avi', '.mov', '.doc', '.docx', '.xls', '.xlsx']

# 伺服器設定
HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", 8000)) 