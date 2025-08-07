import os
import requests
import uuid
from datetime import datetime
from typing import Optional, Tuple
from linebot.models import MessageEvent, FileMessage
import config

class FileHandler:
    def __init__(self):
        # 確保暫存資料夾存在
        if not os.path.exists(config.TEMP_FOLDER):
            os.makedirs(config.TEMP_FOLDER)
    
    def download_file(self, message_event: MessageEvent) -> Optional[Tuple[str, str, int]]:
        """
        下載 LINE 檔案並儲存到本地
        
        Args:
            message_event: LINE 訊息事件
            
        Returns:
            Tuple[檔案路徑, 檔案名稱, 檔案大小] 或 None
        """
        if not isinstance(message_event.message, FileMessage):
            return None
            
        try:
            # 取得檔案內容
            file_content = self._get_file_content(message_event.message.id)
            if not file_content:
                return None
            
            # 取得檔案資訊
            file_name = message_event.message.file_name or f"file_{uuid.uuid4().hex[:8]}"
            file_size = message_event.message.file_size
            
            # 檢查檔案大小
            if file_size > config.MAX_FILE_SIZE:
                raise ValueError(f"檔案大小超過限制 ({config.MAX_FILE_SIZE / 1024 / 1024}MB)")
            
            # 檢查檔案類型
            file_ext = os.path.splitext(file_name)[1].lower()
            if file_ext not in config.SUPPORTED_EXTENSIONS:
                raise ValueError(f"不支援的檔案類型: {file_ext}")
            
            # 生成唯一檔案名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{timestamp}_{uuid.uuid4().hex[:8]}_{file_name}"
            file_path = os.path.join(config.TEMP_FOLDER, unique_filename)
            
            # 儲存檔案
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            return file_path, file_name, file_size
            
        except Exception as e:
            print(f"下載檔案時發生錯誤: {str(e)}")
            return None
    
    def _get_file_content(self, message_id: str) -> Optional[bytes]:
        """
        從 LINE 取得檔案內容
        
        Args:
            message_id: LINE 訊息 ID
            
        Returns:
            檔案內容的 bytes 或 None
        """
        try:
            from linebot import LineBotApi
            line_bot_api = LineBotApi(config.LINE_CHANNEL_ACCESS_TOKEN)
            
            # 取得檔案內容
            file_content = line_bot_api.get_message_content(message_id)
            return file_content.content
            
        except Exception as e:
            print(f"取得檔案內容時發生錯誤: {str(e)}")
            return None
    
    def cleanup_temp_file(self, file_path: str):
        """
        清理暫存檔案
        
        Args:
            file_path: 要刪除的檔案路徑
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"已清理暫存檔案: {file_path}")
        except Exception as e:
            print(f"清理檔案時發生錯誤: {str(e)}")
    
    def get_file_info(self, file_path: str) -> dict:
        """
        取得檔案資訊
        
        Args:
            file_path: 檔案路徑
            
        Returns:
            包含檔案資訊的字典
        """
        try:
            stat = os.stat(file_path)
            return {
                'size': stat.st_size,
                'created_time': datetime.fromtimestamp(stat.st_ctime),
                'modified_time': datetime.fromtimestamp(stat.st_mtime)
            }
        except Exception as e:
            print(f"取得檔案資訊時發生錯誤: {str(e)}")
            return {} 