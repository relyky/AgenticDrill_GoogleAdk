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
HTTP POST /query → FastAPI → ADK Session → ADK Runner → Agent → 工具函式 → 回應串流
```

### 核心元件

| 檔案 | 用途 |
|------|------|
| `main.py` | FastAPI 應用入口，整合 ADK Runner |
| `__init__.py` | 服務常數 (SERVICE_NAME, VERSION) |
| `root_agent/agent.py` | Agent 定義與工具函式 |

### API 端點

- `GET /healthz` - 健康檢查，回傳服務名稱和版本
- `POST /query` - 接收 `{"query": "問題"}` 格式，回傳 Agent 回應

### ADK 整合要點

```python
# Session 和 Artifact 服務使用 In-Memory 實作
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

### 新增 Agent
1. 建立 `{agent_name}/agent.py`
2. 複製 `.env` 範本並設定 API 金鑰
3. 在 `main.py` 中 import

### 新增工具函式
工具函式要求:
- 必須是同步 Python 函式
- 需要完整的 docstring (ADK 用於生成工具描述給 LLM)
- 參數使用型別提示
- 回傳 dict 結構，包含 `status` 欄位

```python
def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city."""
    return {"status": "success", "city": city, "time": "10:30 AM"}
```

### API 測試
```bash
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What time is it in Tokyo?"}'
```

## Google ADK 特定行為

- **Artifacts**: ADK 執行時會在 `.adk/artifacts/` 產生檔案
- **Session 隔離**: 每個 API 請求建立獨立 session，不保留對話歷史
- **Agent 組合**: Agent 可以呼叫其他 Agent 作為工具
- **事件串流**: `run_async` 回傳非同步迭代器，逐步產生回應事件
