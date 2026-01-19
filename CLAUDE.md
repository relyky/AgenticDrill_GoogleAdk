# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概述

基於 Google ADK (Agent Development Kit) v1.15.1 的 AI 代理開發專案，透過 FastAPI 提供 RESTful API 端點。使用 Python 3.12 和 uv 作為套件管理工具。

## 常用指令

```bash
# 初始化環境
uv venv && uv sync

# 啟動虛擬環境
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Unix/macOS

# 開發伺服器 (自動重載)
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Docker 部署
docker-compose up -d
docker-compose logs -f my-adkagent
```

## 環境變數配置

專案使用雙層環境變數結構:
- **專案根目錄 `.env`**: 由 `main.py` 透過 `load_dotenv()` 載入
- **`root_agent/.env`**: Agent 專用環境變數
  - `GOOGLE_API_KEY`: Gemini API 金鑰
  - `GOOGLE_GENAI_USE_VERTEXAI`: 設為 `FALSE` 表示使用 Gemini API (非 Vertex AI)

## 系統架構

### 執行流程
```
HTTP Request → FastAPI (main.py) → Router → ADK Session → ADK Runner → Agent → 工具函式 → 回應串流
```

### 核心元件

| 檔案 | 用途 |
|------|------|
| `main.py` | FastAPI 應用入口，載入環境變數、設定 CORS、註冊 Router |
| `__init__.py` | 服務常數 (SERVICE_NAME, VERSION) |
| `api/routers/` | API 端點模組 (health.py, query.py) |
| `root_agent/agent.py` | Agent 定義，使用 `gemini-3-flash-preview` 模型 |
| `root_agent/tools.py` | Agent 工具函式 (get_system_time, get_weather) |

### API 端點

- `GET /healthz` - 健康檢查，回傳服務名稱和版本
- `POST /query` - 接收 multipart/form-data 格式
  - `userInput`: 用戶查詢文字
  - `files`: 可選，支援多檔上傳 (csv, json, md 等文字檔)

### ADK 整合要點

```python
# Session 和 Artifact 服務使用 In-Memory 實作 (query.py)
session_service = InMemorySessionService()
artifacts_service = InMemoryArtifactService()

# Runner 執行非同步事件串流
runner = Runner(
    app_name="google_adk_drill",
    agent=root_agent,
    session_service=session_service,
    artifact_service=artifacts_service
)
```

## 開發流程

### 新增 Router
1. 在 `api/routers/` 建立新檔案
2. 在 `api/routers/__init__.py` 匯出 router
3. 在 `main.py` 註冊 `app.include_router()`

### 新增 Agent
1. 建立 `{agent_name}/agent.py`
2. 複製 `root_agent/.env` 範本並設定 API 金鑰
3. 在對應 router 中 import

### 新增工具函式
工具函式要求:
- 可以是同步或 async 函式
- 需要完整的 docstring (ADK 用於生成工具描述給 LLM)
- 參數使用型別提示
- 回傳 dict 結構

```python
# 同步範例
def get_system_time() -> dict:
    """Returns the current system time."""
    return {"status": "success", "time": "10:30 AM"}

# 非同步範例
async def get_weather(latitude: float, longitude: float) -> dict:
    """Get weather for coordinates."""
    async with httpx.AsyncClient() as client:
        # ...
```

### API 測試
```bash
# 純文字查詢
curl -X POST http://127.0.0.1:8000/query \
  -F "userInput=What time is it?"

# 含檔案上傳
curl -X POST http://127.0.0.1:8000/query \
  -F "userInput=分析這個檔案" \
  -F "files=@data.csv"
```

## Google ADK 特定行為

- **Artifacts**: ADK 執行時會在 `.adk/artifacts/` 產生檔案
- **Session 隔離**: 每個 API 請求建立獨立 session，不保留對話歷史
- **Agent 組合**: Agent 可以呼叫其他 Agent 作為工具
- **事件串流**: `run_async` 回傳非同步迭代器，逐步產生回應事件
