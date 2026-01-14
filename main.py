import logging
from dotenv import load_dotenv
from google.genai import types
from google.adk.runners import Runner
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from root_agent.agent import root_agent

load_dotenv() # 這會讀取 .env 檔案

# 定義 model
class QueryRequest(BaseModel):
    query: str

# 設定 logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,      # Config.LOG_LEVEL,
    filename=None,            # Config.LOG_FILENAME,
    encoding="utf-8",
)

logger = logging.getLogger(__name__)

# 設定 Google ADK agent
session_service = InMemorySessionService()
artifacts_service = InMemoryArtifactService()


# 設定 FastAPI
app = FastAPI()

# CORS
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

@app.post("/query")
async def handle_query(request: QueryRequest):
    try:
        now = datetime.now()
        
        # 建立新會話
        session = await session_service.create_session(
            state={},
            app_name="google_adk_drill",
            user_id="user"
        )
        
        # 將使用者訊息轉成 ADK Content
        parts = [types.Part(text=request.query)]
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
        async for event in events_async:
            if event.content:
                for part in event.content.parts:
                    if part.text:
                        response.append(part.text)
                        
        responseText = "\n".join(response)
                
        return {
            "received_time": now,
			"responseText": responseText,
		}

    except Exception as e:
        return {"error":str(e)}

#def main():
#    logger.info("系統啟始")
#
#if __name__ == "__main__":
#    main()
