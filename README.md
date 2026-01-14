
## 開發環境準備
```bash
uv init --python 3.12
uv venv
uv add google-adk==1.15.1
```

### 開發偵錯模式啟動
```bash
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000
# 或
uv run uvicorn main:app
```

## Docker 部署

### 前置準備
1. 安裝 Docker Desktop
2. 複製環境變數範本：
   ```bash
   cp .env.example .env
   ```
3. 編輯 `.env` 檔案，填入您的 Google API 金鑰

### 使用 Docker Compose 部署（推薦）
```bash
# 建置並啟動容器
docker-compose up -d

# 查看容器狀態
docker-compose ps

# 查看日誌
docker-compose logs -f my-adkagent

# 停止容器
docker-compose down
```

### 使用 Docker 指令部署
```bash
# 建置映像
docker build -t my-adkagent:latest .

# 執行容器
docker run -d \
  --name my-adkagent \
  -p 8000:8000 \
  --env-file .env \
  my-adkagent:latest

# 查看日誌
docker logs -f my-adkagent

# 停止容器
docker stop my-adkagent
docker rm my-adkagent
```

### 測試 API
```bash
# 測試查詢端點
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello"}'

# 查看 API 文檔
# 瀏覽器開啟: http://localhost:8000/docs
```

## 未來議題
未來可在 FastAPI (main:app) 加上 使用者認證、CORS 限制、背景任務 等等，讓它更完整、更安全。
