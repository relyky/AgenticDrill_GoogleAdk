import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from __init__ import SERVICE_NAME, VERSION
from api.routers import health_router, query_router

load_dotenv() # 這會讀取 .env 檔案

# 設定 logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,      # Config.LOG_LEVEL,
    filename=None,            # Config.LOG_FILENAME,
    encoding="utf-8",
)

logger = logging.getLogger(__name__)

# 設定 FastAPI
app = FastAPI(title=SERVICE_NAME, version=VERSION)

# CORS
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# 註冊 Router
app.include_router(health_router)
app.include_router(query_router)

#def main():
#    logger.info("系統啟始")
#
#if __name__ == "__main__":
#    main()
