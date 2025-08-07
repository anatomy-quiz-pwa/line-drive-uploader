import os
import json
from typing import Optional, Dict
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import config
import mimetypes

credentials = service_account.Credentials.from_service_account_file(
    config.GOOGLE_CREDENTIALS_JSON,
    scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build('drive', 'v3', credentials=credentials)

def upload_file_to_drive(file_path, file_name):
    mime_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
    file_metadata = {
        'name': file_name,
        'parents': [config.UPLOAD_FOLDER_ID]
    }
    media = MediaFileUpload(file_path, mimetype=mime_type)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    return file.get('id'), file.get('webViewLink') 