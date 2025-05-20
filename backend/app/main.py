from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from .api.routes import router as api_router
from .core.config import settings

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def startup_event():
    """应用程序启动事件"""
    logger.info(f"Started {settings.PROJECT_NAME} backend server")
    
    # 检查必要的服务可用性
    services = []
    if settings.HF_AVAILABLE:
        services.append("Hugging Face")
    if settings.MS_AVAILABLE:
        services.append("ModelScope")
        
    if services:
        logger.info(f"Available model services: {', '.join(services)}")
    else:
        logger.warning("No model services are available. Please install huggingface_hub or modelscope.")


@app.on_event("shutdown")
async def shutdown_event():
    """应用程序关闭事件"""
    logger.info(f"Shutting down {settings.PROJECT_NAME} backend server")


@app.get("/")
async def root():
    """根路径响应"""
    return {
        "name": settings.PROJECT_NAME,
        "api_version": "v1",
        "docs": f"{settings.API_V1_STR}/docs",
        "services": {
            "huggingface": settings.HF_AVAILABLE,
            "modelscope": settings.MS_AVAILABLE
        }
    } 