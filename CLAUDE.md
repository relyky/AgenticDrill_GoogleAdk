# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概述

這是一個基於 Google ADK (Agent Development Kit) v1.15.1 的 AI 代理開發專案,透過 FastAPI 提供 RESTful API 端點。使用 Python 3.12 和 uv 作為套件管理工具。

## 環境設定

### 初始化環境
```bash
# 建立虛擬環境
uv venv

# 啟動虛擬環境 (Windows)
.venv\Scripts\activate

# 啟動虛擬環境 (Unix/macOS)
source .venv/bin/activate

# 安裝依賴
uv sync
```

### 啟動開發伺服器
```bash
# 開發模式 (自動重載)
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000

# 或簡化版本
uv run uvicorn main:app
```

### 環境變數配置
專案使用雙層環境變數結構:
- **專案根目錄 `.env`**: 由 `main.py` 透過 `load_dotenv()` 載入,用於全域配置
- **`root_agent/.env`**: Agent 專用環境變數
  - `GOOGLE_API_KEY`: Gemini API 金鑰
  - `GOOGLE_GENAI_USE_VERTEXAI`: 設為 `FALSE` 表示使用 Gemini API (非 Vertex AI)

**重要**: `.env` 檔案包含敏感資訊,已在 `.gitignore` 中排除

## 系統架構

### 執行流程
1. **FastAPI 層** (`main.py`): 接收 HTTP POST 請求至 `/query` 端點
2. **ADK Session 管理**: 每個請求建立獨立的 `InMemorySessionService` 會話
3. **ADK Runner**: 負責執行 Agent,處理訊息流
4. **Agent 執行**: `root_agent` 接收使用者查詢,使用工具函式處理
5. **回應串流**: 收集 Agent 的事件回應並組合成文字回傳

### 核心元件

#### FastAPI 應用 (`main.py`)
- **端點**: `POST /query` 接收 `{"query": "使用者問題"}` 格式
- **CORS**: 允許所有來源 (開發用途)
- **日誌**: 使用 Python logging,DEBUG 層級,UTF-8 編碼

#### ADK 整合架構
```python
# Session 和 Artifact 服務使用 In-Memory 實作
session_service = InMemorySessionService()
artifacts_service = InMemoryArtifactService()

# Runner 串接 Agent 與服務
runner = Runner(
    app_name="google_adk_drill",
    agent=root_agent,  # 從 root_agent.agent 匯入
    session_service=session_service,
    artifact_service=artifacts_service
)

# 執行非同步事件串流
events_async = runner.run_async(
    session_id=session.id,
    user_id="user",
    new_message=content  # types.Content(role="user", parts=[...])
)
```

#### Agent 定義 (`root_agent/agent.py`)
- 使用 `google.adk.agents.llm_agent.Agent` 建立
- 必要參數:
  - `model`: LLM 模型名稱 (如 `gemini-3-flash-preview`)
  - `name`: Agent 識別名稱
  - `description`: 功能簡述
  - `instruction`: 系統提示詞
  - `tools`: 工具函式列表

### 工具函式設計
- 必須是同步 Python 函式
- 需要完整的 docstring (ADK 用於生成工具描述給 LLM)
- 參數使用型別提示
- 回傳 dict 結構,包含 `status` 欄位
- 範例: `def get_current_time(city: str) -> dict`

## 開發流程

### 新增 Agent
1. 建立新目錄 `{agent_name}/`
2. 建立 `agent.py` 定義 Agent 實例
3. 複製 `.env` 範本並設定 API 金鑰
4. 在 `main.py` 中 import: `from {agent_name}.agent import {agent_name}`

### 新增工具函式
1. 在 Agent 模組中定義函式
2. 加入完整 docstring 說明用途、參數、回傳值
3. 在 `Agent(tools=[...])` 中註冊
4. Agent 會自動根據 docstring 生成工具描述

### API 測試
```bash
# 使用 curl 測試
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What time is it in Tokyo?"}'

# 回應格式
{
  "received_time": "2024-01-13T10:30:00",
  "responseText": "Agent 的回應文字"
}
```

## Google ADK 特定行為

- **Artifacts**: ADK 執行時會在 `.adk/artifacts/` 產生檔案
- **Session 隔離**: 每個 API 請求建立獨立 session,不保留對話歷史
- **Agent 組合**: Agent 可以呼叫其他 Agent 作為工具
- **事件串流**: `run_async` 回傳非同步迭代器,逐步產生回應事件
