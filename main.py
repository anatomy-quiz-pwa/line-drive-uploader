from fastapi import FastAPI, Request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, FileMessage, FlexSendMessage
from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
from drive_uploader import upload_file_to_drive
from message_formatter import create_flex_message
import tempfile, os, datetime

app = FastAPI()
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.post("/callback")
async def callback(request: Request):
    body = await request.body()
    signature = request.headers['X-Line-Signature']
    handler.handle(body.decode('utf-8'), signature)
    return 'OK'

@handler.add(MessageEvent, message=FileMessage)
def handle_file_message(event):
    file_name = event.message.file_name
    file_content = line_bot_api.get_message_content(event.message.id)
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        for chunk in file_content.iter_content():
            tmp.write(chunk)
        tmp_path = tmp.name

    file_size = os.path.getsize(tmp_path) / (1024 * 1024)  # MB
    uploaded_at = datetime.datetime.now().strftime('%Y/%m/%d %H:%M')
    file_id, web_link = upload_file_to_drive(tmp_path, file_name)
    flex = create_flex_message(file_name, file_size, web_link, uploaded_at)

    line_bot_api.reply_message(event.reply_token, FlexSendMessage.new_from_json_dict(flex))
    os.remove(tmp_path) 