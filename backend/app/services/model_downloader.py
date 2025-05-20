import os
import re
import shutil
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple, Union, Any, List, Callable
import requests
from ..core.config import settings
from ..services.task_manager import task_manager

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 尝试导入必要的SDK
try:
    from huggingface_hub import snapshot_download, HfApi, hf_hub_url
    from huggingface_hub.utils import HfFolder
    HF_AVAILABLE = True
except ImportError:
    logger.warning("huggingface_hub not installed. Hugging Face downloads will not be available.")
    HF_AVAILABLE = False

try:
    from modelscope.hub.snapshot_download import snapshot_download as ms_snapshot_download
    from modelscope.hub.api import HubApi
    MS_AVAILABLE = True
except ImportError:
    logger.warning("modelscope not installed. ModelScope downloads will not be available.")
    MS_AVAILABLE = False


class ModelDownloader:
    """模型下载器服务类"""
    
    @staticmethod
    def filter_files_by_regex(files: List[str], pattern: str) -> List[str]:
        """
        根据正则表达式过滤文件
        
        Args:
            files: 文件列表
            pattern: 正则表达式模式
            
        Returns:
            过滤后的文件列表
        """
        if not pattern or not files:
            return files
            
        try:
            regex = re.compile(pattern)
            filtered = [f for f in files if regex.search(f)]
            logger.info(f"Filtered files using pattern '{pattern}': {len(filtered)}/{len(files)} files match")
            return filtered
        except re.error as e:
            logger.error(f"Invalid regex pattern '{pattern}': {str(e)}")
            return files  # 如果正则表达式无效则返回原始列表
    
    async def get_model_size_huggingface(self, model_id: str, token: Optional[str] = None) -> Tuple[float, str]:
        """
        获取Hugging Face模型的大小
        
        Args:
            model_id: 模型ID
            token: 认证令牌 (可选)
            
        Returns:
            模型大小(GB)和描述信息的元组
        """
        if not HF_AVAILABLE:
            return 0.0, "Error: huggingface_hub SDK not installed"
        
        logger.info(f"Checking size for Hugging Face model: {model_id}")
        
        total_size_bytes = 0
        error_message = None
        
        try:
            # 方法1: 直接从API获取大小
            hf_api = HfApi()
            api_url = f"https://huggingface.co/api/models/{model_id}"
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            
            logger.info(f"Fetching model metadata from API: {api_url}")
            response = requests.get(api_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"API response received")
                
                # 尝试从不同字段提取大小
                if "usedStorage" in data and data["usedStorage"]:
                    total_size_bytes = int(data["usedStorage"])
                elif "cardData" in data and data["cardData"] and "total_size" in data["cardData"]:
                    total_size_bytes = int(data["cardData"]["total_size"])
                elif "card_data" in data and data["card_data"] and "total_size" in data["card_data"]:
                    total_size_bytes = int(data["card_data"]["total_size"]) 
                elif "config" in data and data["config"] and "total_file_size" in data["config"]:
                    total_size_bytes = int(data["config"]["total_file_size"])
                
                # 如果从API获取到有效大小，就完成了
                if total_size_bytes > 0:
                    total_size_gb = total_size_bytes / (1024 ** 3)
                    return total_size_gb, f"Total size of all weights: {total_size_gb:.2f} GB"
            else:
                error_message = f"API response error: {response.status_code}"
                logger.warning(error_message)
        
        except Exception as e:
            logger.warning(f"Error in method 1: {str(e)}")
            error_message = f"Method 1 failed: {str(e)}"
        
        # 方法2: 如果方法1失败，从文件列表获取大小
        if total_size_bytes == 0:
            try:
                logger.info("Trying method 2: Getting file list and sizes")
                files = []
                
                try:
                    # 直接使用huggingface_hub API而不是REST API
                    hf_api = HfApi()
                    files = hf_api.list_repo_files(repo_id=model_id, repo_type="model", token=token)
                    logger.info(f"Found {len(files)} files")
                except Exception as e:
                    logger.warning(f"Failed to list files: {str(e)}")
                    if "401" in str(e) and token:
                        return 0.0, "Error: Invalid authentication token"
                    elif "401" in str(e):
                        return 0.0, "Error: Authentication required for this model"
                    files = []
                
                # 获取每个文件的大小
                if files:
                    # 检查缓存控制头是否表明是LFS文件
                    sample_file = files[0] if files else None
                    use_lfs_size = False
                    
                    # 准备文件请求的头信息
                    head_headers = {}
                    if token:
                        head_headers["Authorization"] = f"Bearer {token}"
                    
                    if sample_file:
                        try:
                            url = hf_api.hf_hub_url(repo_id=model_id, filename=sample_file, repo_type="model")
                            head = requests.head(url, headers=head_headers, allow_redirects=True)
                            use_lfs_size = "x-linked-size" in head.headers
                            logger.info(f"Using LFS size headers: {use_lfs_size}")
                        except Exception as e:
                            logger.warning(f"Error checking headers: {str(e)}")
                    
                    for file in files:
                        try:
                            if not file or file.endswith('/'):
                                continue
                                
                            url = hf_api.hf_hub_url(repo_id=model_id, filename=file, repo_type="model")
                            head = requests.head(url, headers=head_headers, allow_redirects=True)
                            
                            if use_lfs_size and "x-linked-size" in head.headers:
                                size = int(head.headers["x-linked-size"])
                            elif "content-length" in head.headers:
                                size = int(head.headers["content-length"])
                            else:
                                size = 0
                                
                            if size > 0:
                                logger.info(f"File {file}: {size} bytes")
                                total_size_bytes += size
                        except Exception as e:
                            logger.warning(f"Failed to get size for file {file}: {str(e)}")
                    
                    logger.info(f"Total size calculated from files: {total_size_bytes} bytes")
            except Exception as e:
                logger.warning(f"Error in method 2: {str(e)}")
                if not error_message:
                    error_message = f"Method 2 failed: {str(e)}"
        
        # 计算以GB为单位的大小
        total_size_gb = total_size_bytes / (1024 ** 3) if total_size_bytes and total_size_bytes > 0 else 0.0
        
        # 返回结果
        if total_size_gb > 0:
            return total_size_gb, f"Total size of all weights: {total_size_gb:.2f} GB"
        else:
            error_msg = error_message or "Could not determine model size"
            logger.error(f"Failed to get size for {model_id}: {error_msg}")
            return 0.0, f"Error: {error_msg}"

    async def get_model_size_modelscope(self, model_id: str, token: Optional[str] = None) -> Tuple[float, str]:
        """
        获取ModelScope模型的大小
        
        Args:
            model_id: 模型ID
            token: 认证令牌 (可选)
            
        Returns:
            模型大小(GB)和描述信息的元组
        """
        if not MS_AVAILABLE:
            return 0.0, "Error: modelscope SDK not installed"
        
        ms_api = HubApi()
        if token:
            try:
                ms_api.login(token)
            except Exception as e:
                logger.error(f"Failed to login to ModelScope: {str(e)}")
                return 0.0, f"Error: Failed to login - {str(e)}"
        
        try:
            # 获取模型信息
            model_info = ms_api.get_model(model_id)
            logger.info(f"Model info: {model_info}")
            
            # 获取带有详细信息的模型文件
            files = ms_api.get_model_files(model_id)
            logger.info(f"Model files: {files}")
            
            if not files:
                return 0.0, "Error: No files found in model repository"
            
            total_size_bytes = 0
            for file in files:
                if isinstance(file, dict) and "size" in file:
                    total_size_bytes += int(file["size"])
                    
            total_size_gb = total_size_bytes / (1024 ** 3)
            return total_size_gb, f"Total size of all weights: {total_size_gb:.2f} GB"
            
        except Exception as e:
            logger.error(f"Failed to get model info/files for {model_id}: {str(e)}")
            return 0.0, f"Error: Failed to get model info/files - {str(e)}"

    def download_huggingface_model(self, task_id: str, model_id: str, save_path: Optional[str],
                               token: Optional[str], hf_mirror: Optional[str], file_filter: Optional[str] = None,
                               archive_after: bool = False, target_drive_path: Optional[str] = None,
                               archive_name: Optional[str] = None, archive_format: Optional[str] = "zip") -> None:
        """
        下载Hugging Face模型
        
        Args:
            task_id: 任务ID
            model_id: 模型ID
            save_path: 保存路径
            token: 认证令牌
            hf_mirror: Hugging Face镜像URL
            file_filter: 文件过滤正则表达式
            archive_after: 下载后是否归档
            target_drive_path: 目标驱动器路径
            archive_name: 归档名称
            archive_format: 归档格式
        """
        if not HF_AVAILABLE:
            task_manager.update_task(task_id, 0, 0, "failed")
            logger.error("huggingface_hub SDK not installed")
            return
        
        # 设置保存路径
        if not save_path:
            save_path = os.path.join(settings.DEFAULT_DOWNLOAD_PATH, model_id.split("/")[-1])
            
        save_path = Path(save_path)
        
        # 创建保存目录
        os.makedirs(save_path, exist_ok=True)
        
        # 更新任务状态
        task_manager.update_task(task_id, 0, 100, "downloading")
        
        try:
            # 设置HF API环境
            if token:
                HfFolder.save_token(token)
            
            # 准备下载参数
            download_kwargs = {
                "repo_id": model_id,
                "local_dir": str(save_path),
                "local_dir_use_symlinks": False
            }
            
            # 添加镜像URL（如果提供）
            if hf_mirror:
                download_kwargs["endpoint"] = hf_mirror
            
            # 添加文件过滤（如果提供）
            if file_filter:
                hf_api = HfApi()
                try:
                    # 获取模型文件列表
                    files = hf_api.list_repo_files(repo_id=model_id, repo_type="model", token=token)
                    
                    # 应用过滤器
                    filtered_files = self.filter_files_by_regex(files, file_filter)
                    
                    if filtered_files:
                        download_kwargs["allow_patterns"] = filtered_files
                    else:
                        logger.warning(f"No files matched the filter pattern: {file_filter}")
                        task_manager.update_task(task_id, 0, 0, f"failed: No files matched the filter {file_filter}")
                        return
                        
                except Exception as e:
                    logger.error(f"Error applying file filter: {str(e)}")
                    # 继续而不应用过滤器
            
            # 定义进度回调
            def hf_progress_callback(progress):
                downloaded = int(progress.downloaded_bytes)
                total = int(progress.total_bytes)
                task_manager.update_task(task_id, downloaded, total)
            
            # 添加进度回调
            download_kwargs["progress_callback"] = hf_progress_callback
            
            # 开始下载
            logger.info(f"Starting download of {model_id} to {save_path} with params: {download_kwargs}")
            snapshot_download(**download_kwargs)
            
            # 下载完成，更新状态
            task_manager.update_task(task_id, 100, 100, "completed")
            logger.info(f"Download completed for {model_id}")
            
            # 如果请求了归档，执行归档
            if archive_after and target_drive_path:
                self.archive_and_move(task_id, save_path, Path(target_drive_path),
                                      archive_name or model_id.split("/")[-1],
                                      archive_format)
            
        except Exception as e:
            logger.error(f"Error downloading from Hugging Face: {str(e)}")
            task_manager.update_task(task_id, 0, 0, f"failed: {str(e)}")

    def download_modelscope_model(self, task_id: str, model_id: str, save_path: Optional[str],
                              token: Optional[str], file_filter: Optional[str] = None,
                              archive_after: bool = False, target_drive_path: Optional[str] = None,
                              archive_name: Optional[str] = None, archive_format: Optional[str] = "zip") -> None:
        """
        下载ModelScope模型
        
        Args:
            task_id: 任务ID
            model_id: 模型ID
            save_path: 保存路径
            token: 认证令牌
            file_filter: 文件过滤正则表达式
            archive_after: 下载后是否归档
            target_drive_path: 目标驱动器路径
            archive_name: 归档名称
            archive_format: 归档格式
        """
        if not MS_AVAILABLE:
            task_manager.update_task(task_id, 0, 0, "failed")
            logger.error("modelscope SDK not installed")
            return
        
        # 设置保存路径
        if not save_path:
            save_path = os.path.join(settings.DEFAULT_DOWNLOAD_PATH, model_id.split("/")[-1])
            
        save_path = Path(save_path)
        
        # 创建保存目录
        os.makedirs(save_path, exist_ok=True)
        
        # 更新任务状态
        task_manager.update_task(task_id, 0, 100, "downloading")
        
        try:
            # 准备下载参数
            download_kwargs = {
                "model_id": model_id,
                "local_dir": str(save_path)
            }
            
            # 添加令牌（如果提供）
            if token:
                download_kwargs["user_token"] = token
            
            # ModelScope不直接支持带进度回调的下载，需要自定义下载函数
            # 这里我们使用一个简化的方法
            
            # 获取模型信息以估计总大小
            hub_api = HubApi()
            if token:
                hub_api.login(token)
                
            # 获取文件列表
            files = hub_api.get_model_files(model_id)
            total_size = 0
            
            # 如果需要过滤文件
            if file_filter:
                # 从API返回中提取文件名
                file_names = [f["file_name"] for f in files if isinstance(f, dict) and "file_name" in f]
                
                # 应用过滤器
                filtered_files = self.filter_files_by_regex(file_names, file_filter)
                
                # 如果没有文件匹配过滤器，失败
                if not filtered_files:
                    logger.warning(f"No files matched the filter pattern: {file_filter}")
                    task_manager.update_task(task_id, 0, 0, f"failed: No files matched the filter {file_filter}")
                    return
                
                # 只计算过滤后文件的总大小
                for file in files:
                    if isinstance(file, dict) and "file_name" in file and "size" in file:
                        if file["file_name"] in filtered_files:
                            total_size += int(file["size"])
            else:
                # 计算所有文件的总大小
                for file in files:
                    if isinstance(file, dict) and "size" in file:
                        total_size += int(file["size"])
            
            # 开始下载
            logger.info(f"Starting download of {model_id} to {save_path} with params: {download_kwargs}")
            
            # 执行下载
            ms_snapshot_download(**download_kwargs)
            
            # 下载完成，更新状态
            task_manager.update_task(task_id, total_size, total_size, "completed")
            logger.info(f"Download completed for {model_id}")
            
            # 如果请求了归档，执行归档
            if archive_after and target_drive_path:
                self.archive_and_move(task_id, save_path, Path(target_drive_path),
                                      archive_name or model_id.split("/")[-1],
                                      archive_format)
            
        except Exception as e:
            logger.error(f"Error downloading from ModelScope: {str(e)}")
            task_manager.update_task(task_id, 0, 0, f"failed: {str(e)}")

    def archive_and_move(self, task_id: str, source_folder: Path, target_drive: Path, 
                         archive_name_base: str, archive_format: str = "zip") -> None:
        """
        归档并移动模型文件
        
        Args:
            task_id: 任务ID
            source_folder: 源文件夹路径
            target_drive: 目标驱动器路径
            archive_name_base: 归档基础名称
            archive_format: 归档格式
        """
        try:
            task_manager.update_task(task_id, 0, 0, "archiving")
            
            # 确保目标目录存在
            os.makedirs(target_drive, exist_ok=True)
            
            # 创建归档名称
            archive_path = target_drive / f"{archive_name_base}.{archive_format}"
            
            # 创建归档
            logger.info(f"Creating archive: {archive_path}")
            
            # 使用shutil进行归档
            if archive_format == "zip":
                shutil.make_archive(
                    str(archive_path).replace(".zip", ""), 
                    "zip",
                    root_dir=str(source_folder.parent),
                    base_dir=source_folder.name
                )
            elif archive_format in ["tar", "gztar", "bztar", "xztar"]:
                shutil.make_archive(
                    str(archive_path).replace(f".{archive_format}", ""),
                    archive_format,
                    root_dir=str(source_folder.parent),
                    base_dir=source_folder.name
                )
            else:
                logger.error(f"Unsupported archive format: {archive_format}")
                task_manager.update_task(task_id, 0, 0, f"failed: Unsupported archive format: {archive_format}")
                return
            
            # 归档完成
            task_manager.update_task(task_id, 100, 100, "completed")
            logger.info(f"Archive completed: {archive_path}")
            
        except Exception as e:
            logger.error(f"Error creating archive: {str(e)}")
            task_manager.update_task(task_id, 0, 0, f"failed: {str(e)}")


# 全局下载器实例
model_downloader = ModelDownloader() 