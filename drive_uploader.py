import os
import json
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config import GOOGLE_SERVICE_ACCOUNT_JSON, SHARED_DRIVE_ID
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

# 嘗試刷新憑證
try:
    credentials.refresh(Request())
    print("✅ Google 憑證已刷新")
except Exception as e:
    print(f"⚠️ 憑證刷新失敗: {str(e)}")

drive_service = build('drive', 'v3', credentials=credentials)

# Shared Drive 偵測和驗證
shared_drive_id = None
try:
    if SHARED_DRIVE_ID:
        # 明確指定用這顆 Shared Drive
        print(f"🔒 使用指定的 Shared Drive: {SHARED_DRIVE_ID}")
        # 驗證是否可存取
        drive_service.drives().get(driveId=SHARED_DRIVE_ID).execute()
        shared_drive_id = SHARED_DRIVE_ID
        print("✅ 指定 Shared Drive 可存取")
    else:
        print("🔎 自動搜尋 Shared Drives...")
        drives = drive_service.drives().list(pageSize=10).execute().get('drives', [])
        if drives:
            shared_drive_id = drives[0]['id']
            print(f"🌀 偵測到 Shared Drive：{drives[0]['name']} (ID: {shared_drive_id})")
        else:
            print("⚠️ 未偵測到可用 Shared Drive，將使用個人雲端（Service Account 沒配額，可能失敗）")
except Exception as e:
    print(f"🚨 Shared Drive 驗證失敗（權限或網域政策問題）：{e}")

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
    
    try:
        folder = drive_service.files().create(body=file_metadata, fields='id').execute()
        folder_id = folder.get('id')
        print(f"   ✅ 資料夾建立成功，ID: {folder_id}")
        return folder_id
    except Exception as e:
        print(f"   🚨 建立資料夾失敗: {str(e)}")
        raise e

def find_or_create_folder(folder_name, parent_folder_id=None):
    """尋找資料夾，如果不存在則建立"""
    print(f"🔍 尋找資料夾: {folder_name}")
    
    # 搜尋現有資料夾
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_folder_id:
        query += f" and '{parent_folder_id}' in parents"
    
    try:
        results = drive_service.files().list(
            q=query, 
            fields="files(id, name)",
            includeItemsFromAllDrives=True,
            supportsAllDrives=True
        ).execute()
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

def drive_diagnostics():
    """診斷 Shared Drive 存取狀態"""
    info = {"shared_drive_id": shared_drive_id}
    try:
        if shared_drive_id:
            drv = drive_service.drives().get(driveId=shared_drive_id).execute()
            info["shared_drive_name"] = drv.get("name")
            # 試著列第一層項目
            children = drive_service.files().list(
                corpora='drive',
                driveId=shared_drive_id,
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
                q="trashed=false",
                pageSize=10,
                fields="files(id,name,mimeType)"
            ).execute().get("files", [])
            info["visible_items"] = children
        else:
            info["note"] = "未設定或偵測到 Shared Drive（將用個人雲端，Service Account 無配額）"
    except Exception as e:
        info["error"] = f"{e}"
    return info

def upload_file_to_drive(file_path, file_name):
    print(f"🚀 開始上傳檔案到 Google Drive")
    print(f"   檔案路徑: {file_path}")
    print(f"   檔案名稱: {file_name}")
    
    # 使用已驗證的 Shared Drive ID
    parent_folder_id = shared_drive_id
    
    if parent_folder_id:
        print(f"   📂 使用 Shared Drive ID: {parent_folder_id}")
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
    try:
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        
        file_id = file.get('id')
        web_link = file.get('webViewLink')
        print(f"   ✅ 上傳成功！")
        print(f"   檔案 ID: {file_id}")
        print(f"   網頁連結: {web_link}")
        
        return file_id, web_link
    except Exception as e:
        print(f"   🚨 上傳失敗: {str(e)}")
        raise e 