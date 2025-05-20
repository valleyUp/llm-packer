import os
from typing import Any, Dict, Optional
from pydantic import validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用程序设置类"""
    
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "LLM Weights Downloader API"
    
    # CORS设置
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    
    # 下载设置
    DEFAULT_DOWNLOAD_PATH: str = "./models"
    
    # 环境变量设置
    HUGGINGFACE_TOKEN: Optional[str] = None
    MODELSCOPE_TOKEN: Optional[str] = None
    
    # 可用服务配置
    HF_AVAILABLE: bool = True
    MS_AVAILABLE: bool = True
    
    @validator("HF_AVAILABLE", pre=True)
    def validate_hf_available(cls, v: Any) -> bool:
        try:
            from huggingface_hub import snapshot_download, HfApi, hf_hub_url
            return True
        except ImportError:
            return False
    
    @validator("MS_AVAILABLE", pre=True)
    def validate_ms_available(cls, v: Any) -> bool:
        try:
            from modelscope.hub.snapshot_download import snapshot_download as ms_snapshot_download
            from modelscope.hub.api import HubApi
            return True
        except ImportError:
            return False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings() 