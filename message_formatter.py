from datetime import datetime
from typing import Dict, Optional
from drive_uploader import DriveUploader

class MessageFormatter:
    def __init__(self):
        self.drive_uploader = DriveUploader()
    
    def create_flex_message(self, file_name, file_size_mb, web_link, uploaded_at):
        return {
            "type": "flex",
            "altText": f"已上傳檔案：{file_name}",
            "contents": {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": "✅ 已上傳雲端", "weight": "bold", "size": "xl"},
                        {"type": "text", "text": f"檔案名稱：{file_name}"},
                        {"type": "text", "text": f"大小：{file_size_mb:.2f} MB"},
                        {"type": "text", "text": f"上傳時間：{uploaded_at}"}
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "button",
                            "style": "primary",
                            "action": {
                                "type": "uri",
                                "label": "開啟檔案",
                                "uri": web_link
                            }
                        }
                    ]
                }
            }
        }
    
    def create_upload_error_message(self, error_message: str, file_name: str) -> Dict:
        """
        建立上傳失敗的 Flex Message
        
        Args:
            error_message: 錯誤訊息
            file_name: 檔案名稱
            
        Returns:
            LINE Flex Message 字典
        """
        return {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": "https://cdn-icons-png.flaticon.com/512/1828/1828778.png",
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover",
                "backgroundColor": "#E74C3C"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "text",
                        "text": "❌ 檔案上傳失敗",
                        "weight": "bold",
                        "size": "xl",
                        "color": "#E74C3C"
                    },
                    {
                        "type": "text",
                        "text": f"檔案：{file_name}",
                        "size": "sm",
                        "color": "#555555"
                    },
                    {
                        "type": "text",
                        "text": f"錯誤：{error_message}",
                        "size": "sm",
                        "color": "#E74C3C",
                        "wrap": True
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "text",
                        "text": "請稍後再試或聯繫管理員",
                        "size": "sm",
                        "color": "#555555",
                        "align": "center"
                    }
                ]
            }
        }
    
    def create_file_type_error_message(self, file_name: str, supported_types: list) -> Dict:
        """
        建立檔案類型不支援的錯誤訊息
        
        Args:
            file_name: 檔案名稱
            supported_types: 支援的檔案類型列表
            
        Returns:
            LINE Flex Message 字典
        """
        supported_extensions = ", ".join(supported_types)
        
        return {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": "https://cdn-icons-png.flaticon.com/512/1828/1828778.png",
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover",
                "backgroundColor": "#F39C12"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "text",
                        "text": "⚠️ 不支援的檔案類型",
                        "weight": "bold",
                        "size": "xl",
                        "color": "#F39C12"
                    },
                    {
                        "type": "text",
                        "text": f"檔案：{file_name}",
                        "size": "sm",
                        "color": "#555555"
                    },
                    {
                        "type": "text",
                        "text": f"支援的檔案類型：{supported_extensions}",
                        "size": "sm",
                        "color": "#F39C12",
                        "wrap": True
                    }
                ]
            }
        }
    
    def _get_file_type_icon(self, file_name: str) -> str:
        """
        根據檔案類型取得對應的圖示 URL
        
        Args:
            file_name: 檔案名稱
            
        Returns:
            圖示 URL
        """
        import os
        file_ext = os.path.splitext(file_name)[1].lower()
        
        icon_map = {
            '.pdf': 'https://cdn-icons-png.flaticon.com/512/337/337946.png',
            '.jpg': 'https://cdn-icons-png.flaticon.com/512/337/337953.png',
            '.jpeg': 'https://cdn-icons-png.flaticon.com/512/337/337953.png',
            '.png': 'https://cdn-icons-png.flaticon.com/512/337/337953.png',
            '.gif': 'https://cdn-icons-png.flaticon.com/512/337/337953.png',
            '.mp4': 'https://cdn-icons-png.flaticon.com/512/337/337956.png',
            '.avi': 'https://cdn-icons-png.flaticon.com/512/337/337956.png',
            '.mov': 'https://cdn-icons-png.flaticon.com/512/337/337956.png',
            '.doc': 'https://cdn-icons-png.flaticon.com/512/337/337932.png',
            '.docx': 'https://cdn-icons-png.flaticon.com/512/337/337932.png',
            '.xls': 'https://cdn-icons-png.flaticon.com/512/337/337958.png',
            '.xlsx': 'https://cdn-icons-png.flaticon.com/512/337/337958.png'
        }
        
        return icon_map.get(file_ext, 'https://cdn-icons-png.flaticon.com/512/337/337946.png')
    
    def _get_folder_link(self) -> str:
        """
        取得 Google Drive 資料夾連結
        
        Returns:
            資料夾連結
        """
        folder_info = self.drive_uploader.get_folder_info()
        if folder_info:
            return folder_info['link']
        return "https://drive.google.com" 