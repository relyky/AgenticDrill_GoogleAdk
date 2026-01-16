from fastapi import APIRouter, Form, File, UploadFile
from pydantic import BaseModel
from datetime import datetime
from typing import Any, Optional, List
from google.genai import types
from google.adk.runners import Runner
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService
from root_agent.agent import root_agent

router = APIRouter()

# 定義 model
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    responseText: str = ""
    session_id: str | None = None
    usage: dict | None = None
    total_cost_usd: float | None = None
    error: str | None = None    

# 設定 Google ADK agent
session_service = InMemorySessionService()
artifacts_service = InMemoryArtifactService()

@router.post("/query", response_model=QueryResponse)
async def handle_query(
    # 文字欄位使用 Form() 接收
    userInput: str = Form(...), 
    # 檔案欄位使用 File() 接收，List[UploadFile] 支援多檔上傳
    files: Optional[List[UploadFile]] = File(None)
) -> QueryResponse:
    """
    處理用戶查詢請求，透過 Google ADK (Gemini) 生成回應。

    接收 multipart/form-data 格式的請求，將上傳檔案內容與用戶問題組合後傳送給 ClaudeSDKClient 處理。(未實作)

    Args:
        userInput: 用戶查詢文字
        files: 上傳檔案列表（支援 csv, json, md 文字檔）

    Returns:
        QueryResponse
    """
    try:
        now = datetime.now()
        
        # 建立新會話
        session = await session_service.create_session(
            state={},
            app_name="google_adk_drill",
            user_id="user"
        )
        
        # 將使用者訊息轉成 ADK Content
        parts = [types.Part(text=userInput)]
        content = types.Content(role="user", parts=parts)
        
        # Runner 負責執行 Agent
        runner = Runner(
            app_name="google_adk_drill",
            agent=root_agent,
            session_service=session_service,
            artifact_service=artifacts_service
        )
        
        # 非同步執行
        events_async = runner.run_async(
            session_id=session.id,
            user_id="user",
            new_message=content
        )
        
        # 收集回應
        response = []
        usage_metadata = {}
        async for event in events_async:
            if event.content:
                for part in event.content.parts:
                    if part.text:
                        response.append(part.text)
            
            # 獲取 Token 使用量 (通常在最後一個 event)
            if hasattr(event, 'usage_metadata') and event.usage_metadata:
                try:
                    if hasattr(event.usage_metadata, 'model_dump'):
                        usage_metadata = event.usage_metadata.model_dump()
                    else:
                        usage_metadata = dict(event.usage_metadata)
                except Exception:
                    # 如果轉換失敗，嘗試以字串形式紀錄或忽略
                    pass
                        
        responseText = "\n".join(response)
        
        # 估算成本 (Gemini 3 Flash 價格: Input $0.50/1M, Output $3.00/1M)
        total_cost_usd = 0.0
        if usage_metadata:
            prompt_tokens = usage_metadata.get("prompt_token_count", 0)
            candidate_tokens = usage_metadata.get("candidates_token_count", 0)
            # 計算公式
            total_cost_usd = (prompt_tokens * 0.50 / 1_000_000) + (candidate_tokens * 3.00 / 1_000_000)
        
        # 建立 QueryResponse 物件
        return QueryResponse(
            responseText=responseText,
            session_id=session.id,
            usage=usage_metadata if usage_metadata else None,
            total_cost_usd=total_cost_usd if total_cost_usd > 0 else None
        )

    except Exception as e:
        return QueryResponse(error=str(e))
