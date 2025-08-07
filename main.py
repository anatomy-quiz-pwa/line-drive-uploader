from fastapi import FastAPI, Request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, FileMessage, FlexSendMessage, TextSendMessage
from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
from drive_uploader import upload_file_to_drive
from message_formatter import create_flex_message
import tempfile, os, datetime

app = FastAPI()
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.get("/")
async def root():
    return {"message": "LINE Drive Uploader Bot is running!", "status": "active"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.datetime.now().isoformat()}

@app.post("/callback")
async def callback(request: Request):
    body = await request.body()
    signature = request.headers['X-Line-Signature']
    handler.handle(body.decode('utf-8'), signature)
    return 'OK'

@handler.add(MessageEvent, message=FileMessage)
def handle_file_message(event):
    # Debug 訊息
    source_type = event.source.type
    user_id = event.source.user_id if hasattr(event.source, 'user_id') else 'N/A'
    group_id = event.source.group_id if hasattr(event.source, 'group_id') else 'N/A'
    
    print(f"📥 收到 FileMessage")
    print(f"   檔案名稱: {event.message.file_name}")
    print(f"   來源類型: {source_type}")
    print(f"   使用者 ID: {user_id}")
    print(f"   群組 ID: {group_id}")
    
    file_name = event.message.file_name
    file_content = line_bot_api.get_message_content(event.message.id)
    
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            for chunk in file_content.iter_content():
                tmp.write(chunk)
            tmp_path = tmp.name

        file_size = os.path.getsize(tmp_path) / (1024 * 1024)  # MB
        uploaded_at = datetime.datetime.now().strftime('%Y/%m/%d %H:%M')
        
        print(f"📤 開始上傳檔案: {file_name}")
        file_id, web_link = upload_file_to_drive(tmp_path, file_name)
        flex = create_flex_message(file_name, file_size, web_link, uploaded_at)

        line_bot_api.reply_message(event.reply_token, FlexSendMessage.new_from_json_dict(flex))
        print(f"✅ 成功回覆 Flex 訊息")
        
    except Exception as e:
        error_msg = f"❌ 檔案上傳失敗，請聯絡管理員"
        print(f"🚨 上傳失敗: {str(e)}")
        print(f"   錯誤類型: {type(e).__name__}")
        print(f"   檔案名稱: {file_name}")
        
        try:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=error_msg))
            print(f"✅ 成功回覆錯誤訊息")
        except Exception as reply_error:
            print(f"🚨 回覆錯誤訊息失敗: {str(reply_error)}")
    
    finally:
        # 清理臨時檔案
        if 'tmp_path' in locals():
            try:
                os.remove(tmp_path)
                print(f"🧹 已清理臨時檔案: {tmp_path}")
            except Exception as cleanup_error:
                print(f"⚠️ 清理臨時檔案失敗: {str(cleanup_error)}") 