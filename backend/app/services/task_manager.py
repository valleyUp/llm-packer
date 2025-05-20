import time
from typing import Dict, Any, Optional
from pathlib import Path
import logging
import uuid

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TaskManager:
    """任务管理器类，用于管理和维护下载任务的状态"""

    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}

    def create_task(self, source: str, model_id: str, save_path: Optional[str] = None) -> str:
        """
        创建新的下载任务
        
        Args:
            source: 模型来源（huggingface或modelscope）
            model_id: 模型ID
            save_path: 保存路径
            
        Returns:
            任务ID
        """
        task_id = str(uuid.uuid4())
        current_time = time.time()
        
        self.tasks[task_id] = {
            "taskId": task_id,
            "source": source,
            "modelId": model_id,
            "status": "created",
            "progress": 0.0,
            "downloadedSize": 0,
            "totalSize": 0,
            "speed": 0.0,
            "savePath": save_path,
            "startTime": current_time,
            "lastUpdateTime": current_time,
            "type": "download"
        }
        
        logger.info(f"Created task {task_id} for {source}/{model_id}")
        return task_id

    def create_archive_task(self, source_folder: Path, target_drive: Path, 
                           archive_name: str, archive_format: str) -> str:
        """
        创建新的归档任务
        
        Args:
            source_folder: 源文件夹路径
            target_drive: 目标驱动器路径
            archive_name: 归档名称
            archive_format: 归档格式
            
        Returns:
            任务ID
        """
        task_id = str(uuid.uuid4())
        current_time = time.time()
        
        self.tasks[task_id] = {
            "taskId": task_id,
            "status": "created",
            "progress": 0.0,
            "sourcePath": str(source_folder),
            "targetPath": str(target_drive),
            "archiveName": archive_name,
            "archiveFormat": archive_format,
            "startTime": current_time,
            "lastUpdateTime": current_time,
            "type": "archive"
        }
        
        logger.info(f"Created archive task {task_id} for {source_folder}")
        return task_id

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务信息
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务信息字典，如果没有找到则返回None
        """
        return self.tasks.get(task_id)

    def update_task(self, task_id: str, downloaded_size: int, total_size: int, status: Optional[str] = None) -> None:
        """
        更新任务进度
        
        Args:
            task_id: 任务ID
            downloaded_size: 已下载的字节数
            total_size: 总字节数
            status: 状态文本 (可选)
        """
        if task_id not in self.tasks:
            logger.warning(f"Attempted to update unknown task {task_id}")
            return
            
        task = self.tasks[task_id]
        current_time = time.time()
        
        # 计算下载速度
        time_diff = current_time - task["lastUpdateTime"]
        if time_diff > 0:
            size_diff = downloaded_size - task["downloadedSize"]
            speed = size_diff / time_diff if size_diff > 0 else 0
        else:
            speed = 0
            
        # 计算进度百分比
        progress = (downloaded_size / total_size * 100) if total_size > 0 else 0
        
        # 计算剩余时间估计
        remaining_bytes = total_size - downloaded_size
        est_time_left = (remaining_bytes / speed) if speed > 0 else None
        
        # 格式化剩余时间
        if est_time_left is not None:
            if est_time_left < 60:
                est_time_str = f"{est_time_left:.0f} sec"
            elif est_time_left < 3600:
                est_time_str = f"{est_time_left/60:.1f} min"
            else:
                est_time_str = f"{est_time_left/3600:.1f} hours"
        else:
            est_time_str = None
        
        # 更新任务状态
        task.update({
            "downloadedSize": downloaded_size,
            "totalSize": total_size,
            "progress": min(progress, 100.0),  # 确保不超过100%
            "speed": speed,
            "estimatedTimeLeft": est_time_str,
            "lastUpdateTime": current_time
        })
        
        # 仅当提供了状态时更新它
        if status is not None:
            task["status"] = status
            
        logger.debug(f"Updated task {task_id}: {downloaded_size}/{total_size} bytes, {progress:.1f}%, {speed:.2f} B/s")

    def update_archive_progress(self, task_id: str, progress: float, status: Optional[str] = None) -> None:
        """
        更新归档任务进度
        
        Args:
            task_id: 任务ID
            progress: 进度百分比 (0-100)
            status: 状态文本 (可选)
        """
        if task_id not in self.tasks:
            logger.warning(f"Attempted to update unknown archive task {task_id}")
            return
            
        task = self.tasks[task_id]
        current_time = time.time()
        
        # 更新任务状态
        task.update({
            "progress": min(progress, 100.0),  # 确保不超过100%
            "lastUpdateTime": current_time
        })
        
        # 仅当提供了状态时更新它
        if status is not None:
            task["status"] = status
            
        logger.debug(f"Updated archive task {task_id}: {progress:.1f}%")

    def remove_task(self, task_id: str) -> bool:
        """
        删除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            如果任务被删除则返回True，否则返回False
        """
        if task_id in self.tasks:
            del self.tasks[task_id]
            logger.info(f"Removed task {task_id}")
            return True
        return False


# 全局任务管理器实例
task_manager = TaskManager() 