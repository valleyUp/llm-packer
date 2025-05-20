from typing import Dict, Optional, List, Any
from pydantic import BaseModel, Field


class SizeCheckRequest(BaseModel):
    """模型大小检查请求"""
    source: str
    modelId: str
    authToken: Optional[str] = None


class DownloadTaskRequest(BaseModel):
    """下载任务请求"""
    source: str
    modelId: str
    authToken: Optional[str] = None
    savePath: Optional[str] = None
    hfMirror: Optional[str] = None
    fileFilter: Optional[str] = None  # 文件过滤的正则表达式
    archiveAfter: bool = False
    targetDrivePath: Optional[str] = None
    archiveName: Optional[str] = None
    archiveFormat: Optional[str] = "zip"


class TaskIdRequest(BaseModel):
    """任务ID请求"""
    taskId: str


class ArchiveRequest(BaseModel):
    """存档请求"""
    sourceFolderPath: str
    targetDrivePath: str
    archiveName: Optional[str] = "model_archive"
    archiveFormat: Optional[str] = "zip"


class TaskStatus(BaseModel):
    """任务状态响应"""
    taskId: str
    source: str
    modelId: str
    status: str
    progress: float = 0.0
    downloadedSize: int = 0
    totalSize: int = 0
    speed: float = 0.0
    savePath: Optional[str] = None
    errorMessage: Optional[str] = None
    estimatedTimeLeft: Optional[str] = None
    startTime: Optional[float] = None
    lastUpdateTime: Optional[float] = None
    
    class Config:
        from_attributes = True


class SizeResponse(BaseModel):
    """大小检查响应"""
    sizeGB: float
    message: str 