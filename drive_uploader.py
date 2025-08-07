import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config import GOOGLE_SERVICE_ACCOUNT_JSON, GOOGLE_DRIVE_FOLDER_ID
import mimetypes

# 檢查 GOOGLE_SERVICE_ACCOUNT_JSON 是檔案路徑還是 JSON 字串
if os.path.exists(GOOGLE_SERVICE_ACCOUNT_JSON):
    # 如果是檔案路徑
    credentials = service_account.Credentials.from_service_account_file(
        GOOGLE_SERVICE_ACCOUNT_JSON,
        scopes=["https://www.googleapis.com/auth/drive"]
    )
else:
    # 如果是 JSON 字串
    credentials_info = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=["https://www.googleapis.com/auth/drive"]
    )

drive_service = build('drive', 'v3', credentials=credentials)

def upload_file_to_drive(file_path, file_name):
    mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
    file_metadata = {
        'name': file_name,
        'parents': [GOOGLE_DRIVE_FOLDER_ID]
    }
    media = MediaFileUpload(file_path, mimetype=mime_type)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    return file.get('id'), file.get('webViewLink') 