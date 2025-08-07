# LINE File Uploader Bot

一個 LINE Bot，用於監測群組中傳送的檔案（如 PDF、圖片、影片），自動下載並上傳至 Google Drive，並將上傳結果回傳至群組中，避免檔案過期遺失。

## 🚀 功能特色

- 📁 **自動檔案監測**：監測 LINE 群組中的檔案訊息
- ☁️ **Google Drive 上傳**：自動上傳檔案至指定的 Google Drive 資料夾
- 📱 **美觀的回覆訊息**：使用 LINE Flex Message 顯示上傳結果
- 🔗 **檔案連結分享**：提供直接開啟檔案的連結
- 🛡️ **檔案類型驗證**：只處理支援的檔案類型
- 📏 **檔案大小限制**：防止過大檔案影響系統效能
- 🧹 **自動清理**：處理完成後自動清理暫存檔案

## 📋 支援的檔案類型

- **文件**：PDF, DOC, DOCX, XLS, XLSX
- **圖片**：JPG, JPEG, PNG, GIF
- **影片**：MP4, AVI, MOV

## 🛠️ 安裝與設定

### 1. 克隆專案

```bash
git clone <repository-url>
cd line-file-uploader
```

### 2. 安裝依賴

```bash
pip install -r requirements.txt
```

### 3. 設定環境變數

複製 `env.example` 為 `.env` 並填入你的設定：

```bash
cp env.example .env
```

編輯 `.env` 檔案：

```env
# LINE Bot 設定
LINE_CHANNEL_SECRET=你的_LINE_Channel_Secret
LINE_CHANNEL_ACCESS_TOKEN=你的_LINE_Channel_Access_Token

# Google Drive 設定
GOOGLE_CREDENTIALS_JSON=path/to/your/service-account-key.json
UPLOAD_FOLDER_ID=你的_Google_Drive_資料夾_ID

# 伺服器設定（可選）
PORT=8000
```

### 4. LINE Bot 設定

1. 前往 [LINE Developers Console](https://developers.line.biz/)
2. 建立新的 Provider 和 Channel
3. 取得 Channel Secret 和 Channel Access Token
4. 設定 Webhook URL（部署後設定）

### 5. Google Drive API 設定

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用 Google Drive API
4. 建立服務帳戶並下載 JSON 憑證檔案
5. 將憑證檔案放在專案目錄中，或將 JSON 內容直接填入環境變數
6. 在 Google Drive 中建立目標資料夾，並取得資料夾 ID

## 🚀 本地執行

```bash
python main.py
```

伺服器將在 `http://localhost:8000` 啟動。

## ☁️ 雲端部署

### Render 部署

1. 將專案推送到 GitHub
2. 在 Render 中建立新的 Web Service
3. 連接 GitHub 倉庫
4. 設定環境變數
5. 部署

### Railway 部署

1. 將專案推送到 GitHub
2. 在 Railway 中建立新專案
3. 連接 GitHub 倉庫
4. 設定環境變數
5. 部署

### 環境變數設定（雲端部署）

在雲端平台中設定以下環境變數：

- `LINE_CHANNEL_SECRET`
- `LINE_CHANNEL_ACCESS_TOKEN`
- `GOOGLE_CREDENTIALS_JSON`（JSON 字串格式）
- `UPLOAD_FOLDER_ID`
- `PORT`（平台自動設定）

## 📱 使用方式

1. 將機器人加入 LINE 群組
2. 在群組中傳送檔案
3. 機器人會自動處理並回傳上傳結果

### 指令說明

- `help` / `幫助` / `說明`：顯示使用說明
- `status` / `狀態`：檢查系統狀態

## 📁 專案結構

```
line-file-uploader/
├── main.py              # 主程式入口點
├── config.py            # 配置設定
├── file_handler.py      # 檔案處理模組
├── drive_uploader.py    # Google Drive 上傳模組
├── message_formatter.py # LINE 訊息格式化模組
├── requirements.txt     # Python 依賴套件
├── env.example          # 環境變數範例
├── README.md           # 專案說明
└── temp_files/         # 暫存檔案目錄（自動建立）
```

## 🔧 自訂設定

### 修改支援的檔案類型

在 `config.py` 中修改 `SUPPORTED_EXTENSIONS`：

```python
SUPPORTED_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.mp4', '.avi', '.mov', '.doc', '.docx', '.xls', '.xlsx']
```

### 修改檔案大小限制

在 `config.py` 中修改 `MAX_FILE_SIZE`：

```python
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
```

### 自訂 Flex Message 樣式

在 `message_formatter.py` 中修改訊息格式和樣式。

## 🐛 故障排除

### 常見問題

1. **LINE Webhook 驗證失敗**
   - 檢查 Channel Secret 是否正確
   - 確認 Webhook URL 設定正確

2. **Google Drive 上傳失敗**
   - 檢查服務帳戶憑證是否正確
   - 確認 Google Drive API 已啟用
   - 檢查目標資料夾 ID 是否正確

3. **檔案下載失敗**
   - 檢查 LINE Channel Access Token 是否正確
   - 確認檔案大小在限制範圍內

### 日誌查看

應用程式會輸出詳細的日誌資訊，可用於除錯：

```bash
python main.py
```

## 📄 授權

本專案採用 MIT 授權條款。

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📞 支援

如有問題或建議，請提交 Issue 或聯繫開發者。 