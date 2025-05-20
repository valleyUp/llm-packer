from fastapi import APIRouter, BackgroundTasks, HTTPException
from pathlib import Path
import logging
from ..models.schemas import (
    SizeCheckRequest, 
    DownloadTaskRequest, 
    TaskIdRequest,
    ArchiveRequest,
    SizeResponse,
    TaskStatus
)
from ..services.task_manager import task_manager
from ..services.model_downloader import model_downloader

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/check-size", response_model=SizeResponse)
async def check_size_endpoint(request: SizeCheckRequest):
    """检查模型大小的端点"""
    try:
        if request.source == "huggingface":
            size_gb, message = await model_downloader.get_model_size_huggingface(request.modelId, request.authToken)
        elif request.source == "modelscope":
            size_gb, message = await model_downloader.get_model_size_modelscope(request.modelId, request.authToken)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported source: {request.source}")
            
        return SizeResponse(sizeGB=size_gb, message=message)
    except Exception as e:
        logger.error(f"Error in check_size_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/download/start", response_model=TaskStatus)
async def start_download_endpoint(request: DownloadTaskRequest, background_tasks: BackgroundTasks):
    """启动下载任务的端点"""
    try:
        # 创建新的下载任务
        task_id = task_manager.create_task(request.source, request.modelId, request.savePath)
        
        if request.source == "huggingface":
            # 启动Hugging Face下载任务
            background_tasks.add_task(
                model_downloader.download_huggingface_model,
                task_id,
                request.modelId,
                request.savePath,
                request.authToken,
                request.hfMirror,
                request.fileFilter,
                request.archiveAfter,
                request.targetDrivePath,
                request.archiveName,
                request.archiveFormat
            )
        elif request.source == "modelscope":
            # 启动ModelScope下载任务
            background_tasks.add_task(
                model_downloader.download_modelscope_model,
                task_id,
                request.modelId,
                request.savePath,
                request.authToken,
                request.fileFilter,
                request.archiveAfter,
                request.targetDrivePath,
                request.archiveName,
                request.archiveFormat
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported source: {request.source}")
            
        # 获取并返回任务状态
        task_status = task_manager.get_task(task_id)
        if not task_status:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
            
        return TaskStatus(**task_status)
    except Exception as e:
        logger.error(f"Error in start_download_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/archive", response_model=TaskStatus)
async def archive_and_move_endpoint(request: ArchiveRequest, background_tasks: BackgroundTasks):
    """归档和移动模型的端点"""
    try:
        source_folder = Path(request.sourceFolderPath)
        target_drive = Path(request.targetDrivePath)
        
        if not source_folder.exists() or not source_folder.is_dir():
            raise HTTPException(status_code=400, detail=f"Source folder does not exist: {source_folder}")
        
        # 创建新的归档任务
        task_id = task_manager.create_archive_task(
            source_folder,
            target_drive,
            request.archiveName,
            request.archiveFormat
        )
        
        # 启动归档任务
        background_tasks.add_task(
            model_downloader.archive_and_move,
            task_id,
            source_folder,
            target_drive,
            request.archiveName,
            request.archiveFormat
        )
        
        # 获取并返回任务状态
        task_status = task_manager.get_task(task_id)
        if not task_status:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
            
        return TaskStatus(**task_status)
    except Exception as e:
        logger.error(f"Error in archive_and_move_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/progress/{task_id}", response_model=TaskStatus)
async def get_download_progress_endpoint(task_id: str):
    """获取下载进度的端点"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    return TaskStatus(**task)


@router.post("/download/cancel/{task_id}")
async def cancel_download_endpoint(task_id: str):
    """取消下载任务的端点"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
    # 更新状态为已取消
    task_manager.update_task(task_id, task.get("downloadedSize", 0), task.get("totalSize", 0), "cancelled")
    
    return {"status": "success", "message": f"Task {task_id} cancelled"}


@router.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "ok",
        "services": {
            "huggingface": "available" if model_downloader.HF_AVAILABLE else "unavailable",
            "modelscope": "available" if model_downloader.MS_AVAILABLE else "unavailable"
        }
    } 