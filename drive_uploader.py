import os
import json
from typing import Optional, Dict
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import config

class DriveUploader:
    def __init__(self):
        self.service = self._create_drive_service()
    
    def _create_drive_service(self):
        """
        建立 Google Drive API 服務
        
        Returns:
            Google Drive API 服務實例
        """
        try:
            # 讀取服務帳戶憑證
            if os.path.exists(config.GOOGLE_CREDENTIALS_JSON):
                # 如果是檔案路徑
                credentials = service_account.Credentials.from_service_account_file(
                    config.GOOGLE_CREDENTIALS_JSON,
                    scopes=['https://www.googleapis.com/auth/drive.file']
                )
            else:
                # 如果是 JSON 字串
                credentials_info = json.loads(config.GOOGLE_CREDENTIALS_JSON)
                credentials = service_account.Credentials.from_service_account_info(
                    credentials_info,
                    scopes=['https://www.googleapis.com/auth/drive.file']
                )
            
            # 建立 Drive API 服務
            service = build('drive', 'v3', credentials=credentials)
            return service
            
        except Exception as e:
            print(f"建立 Google Drive 服務時發生錯誤: {str(e)}")
            return None
    
    def upload_file(self, file_path: str, file_name: str) -> Optional[Dict]:
        """
        上傳檔案到 Google Drive
        
        Args:
            file_path: 本地檔案路徑
            file_name: 檔案名稱
            
        Returns:
            包含上傳結果的字典或 None
        """
        if not self.service:
            print("Google Drive 服務未初始化")
            return None
        
        try:
            # 準備檔案中繼資料
            file_metadata = {
                'name': file_name,
                'parents': [config.UPLOAD_FOLDER_ID] if config.UPLOAD_FOLDER_ID else []
            }
            
            # 準備媒體檔案
            media = MediaFileUpload(
                file_path,
                resumable=True,
                chunksize=1024*1024  # 1MB chunks
            )
            
            # 上傳檔案
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,size,webViewLink,createdTime'
            ).execute()
            
            # 設定檔案權限為任何人都可以查看
            self.service.permissions().create(
                fileId=file['id'],
                body={'type': 'anyone', 'role': 'reader'},
                fields='id'
            ).execute()
            
            return {
                'file_id': file['id'],
                'file_name': file['name'],
                'file_size': int(file.get('size', 0)),
                'web_view_link': file['webViewLink'],
                'created_time': file['createdTime']
            }
            
        except HttpError as e:
            print(f"Google Drive API 錯誤: {str(e)}")
            return None
        except Exception as e:
            print(f"上傳檔案時發生錯誤: {str(e)}")
            return None
    
    def format_file_size(self, size_bytes: int) -> str:
        """
        格式化檔案大小顯示
        
        Args:
            size_bytes: 檔案大小（bytes）
            
        Returns:
            格式化後的檔案大小字串
        """
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        import math
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def get_folder_info(self) -> Optional[Dict]:
        """
        取得目標資料夾資訊
        
        Returns:
            資料夾資訊字典或 None
        """
        if not self.service or not config.UPLOAD_FOLDER_ID:
            return None
        
        try:
            folder = self.service.files().get(
                fileId=config.UPLOAD_FOLDER_ID,
                fields='id,name,webViewLink'
            ).execute()
            
            return {
                'id': folder['id'],
                'name': folder['name'],
                'link': folder['webViewLink']
            }
            
        except Exception as e:
            print(f"取得資料夾資訊時發生錯誤: {str(e)}")
            return None 