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

def create_folder(folder_name, parent_folder_id=None):
    """建立 Google Drive 資料夾"""
    print(f"📁 建立資料夾: {folder_name}")
    
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    
    # 如果有指定父資料夾，則加入
    if parent_folder_id:
        file_metadata['parents'] = [parent_folder_id]
        print(f"   父資料夾 ID: {parent_folder_id}")
    
    folder = drive_service.files().create(body=file_metadata, fields='id').execute()
    folder_id = folder.get('id')
    
    print(f"   ✅ 資料夾建立成功，ID: {folder_id}")
    return folder_id

def find_or_create_folder(folder_name, parent_folder_id=None):
    """尋找資料夾，如果不存在則建立"""
    print(f"🔍 尋找資料夾: {folder_name}")
    
    # 搜尋現有資料夾
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_folder_id:
        query += f" and '{parent_folder_id}' in parents"
    
    try:
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        
        if files:
            folder_id = files[0]['id']
            print(f"   ✅ 找到現有資料夾，ID: {folder_id}")
            return folder_id
        else:
            print(f"   📁 資料夾不存在，建立新資料夾")
            return create_folder(folder_name, parent_folder_id)
    except Exception as e:
        print(f"   ⚠️ 搜尋資料夾失敗: {str(e)}")
        print(f"   📁 直接建立新資料夾")
        return create_folder(folder_name, parent_folder_id)

def get_shared_drives():
    """取得可用的 Shared Drives"""
    print("🔍 搜尋可用的 Shared Drives...")
    try:
        drives = drive_service.drives().list(fields="drives(id, name)").execute()
        shared_drives = drives.get('drives', [])
        print(f"   ✅ 找到 {len(shared_drives)} 個 Shared Drives")
        for drive in shared_drives:
            print(f"      - {drive['name']} (ID: {drive['id']})")
        return shared_drives
    except Exception as e:
        print(f"   ⚠️ 無法取得 Shared Drives: {str(e)}")
        return []

def upload_file_to_drive(file_path, file_name):
    print(f"🚀 開始上傳檔案到 Google Drive")
    print(f"   檔案路徑: {file_path}")
    print(f"   檔案名稱: {file_name}")
    
    # 嘗試使用 Shared Drive
    shared_drives = get_shared_drives()
    parent_folder_id = None
    
    if shared_drives:
        # 使用第一個 Shared Drive
        parent_folder_id = shared_drives[0]['id']
        print(f"   📂 使用 Shared Drive: {shared_drives[0]['name']}")
    else:
        print(f"   📂 沒有找到 Shared Drive，使用個人 Google Drive")
    
    # 自動建立或尋找上傳資料夾
    try:
        upload_folder_id = find_or_create_folder("LINE 自動上傳", parent_folder_id)
        print(f"   目標資料夾 ID: {upload_folder_id}")
    except Exception as e:
        print(f"   ⚠️ Shared Drive 建立資料夾失敗: {str(e)}")
        print(f"   📂 改用個人 Google Drive")
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