import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config import GOOGLE_SERVICE_ACCOUNT_JSON
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

def create_folder(folder_name):
    """建立 Google Drive 資料夾"""
    print(f"📁 建立資料夾: {folder_name}")
    
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    
    folder = drive_service.files().create(body=file_metadata, fields='id').execute()
    folder_id = folder.get('id')
    
    print(f"   ✅ 資料夾建立成功，ID: {folder_id}")
    return folder_id

def find_or_create_folder(folder_name):
    """尋找資料夾，如果不存在則建立"""
    print(f"🔍 尋找資料夾: {folder_name}")
    
    # 搜尋現有資料夾
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    
    if files:
        folder_id = files[0]['id']
        print(f"   ✅ 找到現有資料夾，ID: {folder_id}")
        return folder_id
    else:
        print(f"   📁 資料夾不存在，建立新資料夾")
        return create_folder(folder_name)

def upload_file_to_drive(file_path, file_name):
    print(f"🚀 開始上傳檔案到 Google Drive")
    print(f"   檔案路徑: {file_path}")
    print(f"   檔案名稱: {file_name}")
    
    # 自動建立或尋找上傳資料夾
    upload_folder_id = find_or_create_folder("LINE 自動上傳")
    print(f"   目標資料夾 ID: {upload_folder_id}")
    
    mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
    print(f"   MIME 類型: {mime_type}")
    
    file_metadata = {
        'name': file_name,
        'parents': [upload_folder_id]
    }
    media = MediaFileUpload(file_path, mimetype=mime_type)
    
    print(f"   📤 執行上傳...")
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    
    file_id = file.get('id')
    web_link = file.get('webViewLink')
    print(f"   ✅ 上傳成功！")
    print(f"   檔案 ID: {file_id}")
    print(f"   網頁連結: {web_link}")
    
    return file_id, web_link 