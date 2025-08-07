from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, FileMessage, TextMessage
import logging
import traceback

from config import LINE_CHANNEL_SECRET, LINE_CHANNEL_ACCESS_TOKEN, HOST, PORT
from file_handler import FileHandler
from drive_uploader import DriveUploader
from message_formatter import MessageFormatter

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 建立 FastAPI 應用程式
app = FastAPI(title="LINE File Uploader Bot", version="1.0.0")

# 初始化 LINE Bot
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 初始化各個處理器
file_handler = FileHandler()
drive_uploader = DriveUploader()
message_formatter = MessageFormatter()

@app.get("/")
async def root():
    """健康檢查端點"""
    return {"message": "LINE File Uploader Bot is running!", "status": "healthy"}

@app.post("/webhook")
async def webhook(request: Request):
    """LINE Webhook 端點"""
    try:
        # 取得請求內容
        body = await request.body()
        signature = request.headers.get('X-Line-Signature', '')
        
        # 驗證簽名
        try:
            handler.handle(body.decode('utf-8'), signature)
        except InvalidSignatureError:
            logger.error("Invalid signature")
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        return JSONResponse(content={"status": "ok"})
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")

@handler.add(MessageEvent, message=FileMessage)
def handle_file_message(event):
    """處理檔案訊息"""
    try:
        logger.info(f"收到檔案訊息: {event.message.file_name}")
        
        # 下載檔案
        download_result = file_handler.download_file(event)
        if not download_result:
            logger.error("檔案下載失敗")
            return
        
        file_path, file_name, file_size = download_result
        logger.info(f"檔案下載成功: {file_name} ({file_size} bytes)")
        
        try:
            # 上傳到 Google Drive
            upload_result = drive_uploader.upload_file(file_path, file_name)
            
            if upload_result:
                # 建立成功訊息
                flex_message = message_formatter.create_upload_success_message(
                    upload_result, file_name
                )
                
                # 回傳成功訊息
                line_bot_api.reply_message(
                    event.reply_token,
                    {
                        "type": "flex",
                        "altText": f"檔案 {file_name} 已成功上傳至 Google Drive",
                        "contents": flex_message
                    }
                )
                
                logger.info(f"檔案上傳成功: {file_name}")
                
            else:
                # 建立錯誤訊息
                error_message = message_formatter.create_upload_error_message(
                    "上傳到 Google Drive 失敗", file_name
                )
                
                line_bot_api.reply_message(
                    event.reply_token,
                    {
                        "type": "flex",
                        "altText": f"檔案 {file_name} 上傳失敗",
                        "contents": error_message
                    }
                )
                
                logger.error(f"檔案上傳失敗: {file_name}")
                
        except Exception as e:
            logger.error(f"上傳過程中發生錯誤: {str(e)}")
            
            # 建立錯誤訊息
            error_message = message_formatter.create_upload_error_message(
                str(e), file_name
            )
            
            line_bot_api.reply_message(
                event.reply_token,
                {
                    "type": "flex",
                    "altText": f"檔案 {file_name} 處理失敗",
                    "contents": error_message
                }
            )
        
        finally:
            # 清理暫存檔案
            file_handler.cleanup_temp_file(file_path)
            
    except Exception as e:
        logger.error(f"處理檔案訊息時發生錯誤: {str(e)}")
        logger.error(traceback.format_exc())
        
        # 回傳一般錯誤訊息
        try:
            line_bot_api.reply_message(
                event.reply_token,
                {
                    "type": "text",
                    "text": "處理檔案時發生錯誤，請稍後再試。"
                }
            )
        except:
            pass

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    """處理文字訊息"""
    text = event.message.text.strip()
    
    if text.lower() in ['help', '幫助', '說明']:
        help_message = """📁 LINE 檔案上傳機器人

🔧 功能說明：
• 自動監測群組中的檔案訊息
• 支援 PDF、圖片、影片、Office 檔案
• 自動上傳至 Google Drive
• 回傳檔案連結和資訊

📋 支援的檔案類型：
• 文件：PDF, DOC, DOCX, XLS, XLSX
• 圖片：JPG, JPEG, PNG, GIF
• 影片：MP4, AVI, MOV

📏 檔案大小限制：50MB

💡 使用方式：
直接在群組中傳送檔案即可，機器人會自動處理！

如有問題請聯繫管理員。"""
        
        line_bot_api.reply_message(
            event.reply_token,
            {"type": "text", "text": help_message}
        )
    
    elif text.lower() in ['status', '狀態']:
        # 檢查 Google Drive 連接狀態
        folder_info = drive_uploader.get_folder_info()
        if folder_info:
            status_message = f"✅ 系統狀態正常\n📁 目標資料夾：{folder_info['name']}"
        else:
            status_message = "❌ Google Drive 連接異常，請檢查設定"
        
        line_bot_api.reply_message(
            event.reply_token,
            {"type": "text", "text": status_message}
        )

if __name__ == "__main__":
    import uvicorn
    logger.info(f"啟動 LINE File Uploader Bot 於 {HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT) 