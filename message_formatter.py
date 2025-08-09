def create_flex_message(file_name, file_size_mb, web_link, uploaded_at):
    return {
        "type": "flex",
        "altText": f"已上傳檔案：{file_name}",
        "contents": {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "icon",
                                "url": "https://drive.google.com/favicon.ico",
                                "size": "lg"
                            },
                            {
                                "type": "text",
                                "text": "已上傳雲端",
                                "weight": "bold",
                                "size": "xl"
                            }
                        ],
                        "spacing": "sm"
                    },
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