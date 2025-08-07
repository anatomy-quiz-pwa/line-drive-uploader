from datetime import datetime
from typing import Dict, Optional
from drive_uploader import DriveUploader

class MessageFormatter:
    def __init__(self):
        self.drive_uploader = DriveUploader()
    
    def create_upload_success_message(self, upload_result: Dict, original_file_name: str) -> Dict:
        """
        建立上傳成功的 Flex Message
        
        Args:
            upload_result: 上傳結果字典
            original_file_name: 原始檔案名稱
            
        Returns:
            LINE Flex Message 字典
        """
        # 格式化檔案大小
        file_size = self.drive_uploader.format_file_size(upload_result['file_size'])
        
        # 格式化上傳時間
        upload_time = datetime.fromisoformat(upload_result['created_time'].replace('Z', '+00:00'))
        formatted_time = upload_time.strftime("%Y/%m/%d %H:%M")
        
        # 取得檔案類型圖示
        icon_url = self._get_file_type_icon(original_file_name)
        
        return {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": icon_url,
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover",
                "backgroundColor": "#27AE60"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "text",
                        "text": "✅ 檔案已上傳至雲端",
                        "weight": "bold",
                        "size": "xl",
                        "color": "#27AE60"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "spacing": "xs",
                        "margin": "lg",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "📄 檔案名稱",
                                        "size": "sm",
                                        "color": "#555555",
                                        "flex": 0
                                    },
                                    {
                                        "type": "text",
                                        "text": original_file_name,
                                        "size": "sm",
                                        "color": "#111111",
                                        "flex": 1,
                                        "wrap": True
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "📊 檔案大小",
                                        "size": "sm",
                                        "color": "#555555",
                                        "flex": 0
                                    },
                                    {
                                        "type": "text",
                                        "text": file_size,
                                        "size": "sm",
                                        "color": "#111111",
                                        "flex": 1
                                    }
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "horizontal",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "⏰ 上傳時間",
                                        "size": "sm",
                                        "color": "#555555",
                                        "flex": 0
                                    },
                                    {
                                        "type": "text",
                                        "text": formatted_time,
                                        "size": "sm",
                                        "color": "#111111",
                                        "flex": 1
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "color": "#27AE60",
                        "action": {
                            "type": "uri",
                            "label": "🔗 開啟檔案連結",
                            "uri": upload_result['web_view_link']
                        }
                    },
                    {
                        "type": "button",
                        "style": "secondary",
                        "action": {
                            "type": "uri",
                            "label": "📁 查看資料夾",
                            "uri": self._get_folder_link()
                        }
                    }
                ],
                "flex": 0
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