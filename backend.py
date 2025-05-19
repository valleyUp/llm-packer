import os
import sys
import json
import re
from typing import Dict, Optional, Tuple, Union, Any, List
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from pathlib import Path
import requests
from fastapi.responses import JSONResponse
import uuid
import time
import shutil # For archiving

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global dict to store download task states
download_tasks: Dict[str, Dict[str, Any]] = {}

# Try to import required SDKs, handle missing dependencies gracefully
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

app = FastAPI(title="LLM Weights Downloader API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Pydantic models for request validation
class SizeCheckRequest(BaseModel):
    source: str
    modelId: str
    authToken: Optional[str] = None

class DownloadTaskRequest(BaseModel):
    source: str
    modelId: str
    authToken: Optional[str] = None
    savePath: Optional[str] = None
    hfMirror: Optional[str] = None
    fileFilter: Optional[str] = None  # Regex pattern for filtering files
    archiveAfter: bool = False
    targetDrivePath: Optional[str] = None
    archiveName: Optional[str] = None
    archiveFormat: Optional[str] = "zip"

class TaskIdRequest(BaseModel):
    taskId: str

class ArchiveRequest(BaseModel):
    sourceFolderPath: str
    targetDrivePath: str
    archiveName: Optional[str] = "model_archive"
    archiveFormat: Optional[str] = "zip"

async def get_model_size_huggingface(model_id: str, token: Optional[str] = None) -> Tuple[float, str]:
    """
    Calculate the total size of all files in a Hugging Face model repository.
    Returns size in GB and a status message.
    """
    try:
        if not HF_AVAILABLE:
            return 0.0, "Error: huggingface_hub SDK not installed"
        
        logger.info(f"Starting size calculation for Hugging Face model: {model_id}")
        
        total_size_bytes = 0
        error_message = None
        
        try:
            # Method 1: Get size from API directly
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
                
                # Try to extract size from different fields
                if "usedStorage" in data and data["usedStorage"]:
                    total_size_bytes = int(data["usedStorage"])
                    logger.info(f"Size found in usedStorage: {total_size_bytes}")
                elif "cardData" in data and data["cardData"] and "total_size" in data["cardData"]:
                    total_size_bytes = int(data["cardData"]["total_size"])
                    logger.info(f"Size found in cardData.total_size: {total_size_bytes}")
                elif "card_data" in data and data["card_data"] and "total_size" in data["card_data"]:
                    total_size_bytes = int(data["card_data"]["total_size"]) 
                    logger.info(f"Size found in card_data.total_size: {total_size_bytes}")
                elif "config" in data and data["config"] and "total_file_size" in data["config"]:
                    total_size_bytes = int(data["config"]["total_file_size"])
                    logger.info(f"Size found in config.total_file_size: {total_size_bytes}")
                
                # If we got a valid size from API, we're done
                if total_size_bytes > 0:
                    total_size_gb = total_size_bytes / (1024 ** 3)
                    return total_size_gb, f"Total size of all weights: {total_size_gb:.2f} GB"
            else:
                error_message = f"API response error: {response.status_code}"
                logger.warning(error_message)
        
        except Exception as e:
            logger.warning(f"Error in method 1: {str(e)}")
            error_message = f"Method 1 failed: {str(e)}"
        
        # Method 2: Get size from list_repo_files if method 1 failed
        if total_size_bytes == 0:
            try:
                logger.info("Trying method 2: Getting file list and sizes")
                files = []
                
                try:
                    # Use huggingface_hub API directly instead of REST API
                    hf_api = HfApi()
                    files = hf_api.list_repo_files(repo_id=model_id, repo_type="model", token=token)
                    logger.info(f"Found {len(files)} files")
                except Exception as e:
                    logger.warning(f"Failed to list files: {str(e)}")
                    # If we get an auth error but have a token, token might be invalid
                    if "401" in str(e) and token:
                        return 0.0, "Error: Invalid authentication token"
                    elif "401" in str(e):
                        return 0.0, "Error: Authentication required for this model"
                    files = []
                
                # Get size for each file
                if files:
                    # Check if cache-control header indicates LFS files
                    sample_file = files[0] if files else None
                    use_lfs_size = False
                    
                    # Prepare headers for file requests
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
        
        # Calculate size in GB
        total_size_gb = total_size_bytes / (1024 ** 3) if total_size_bytes and total_size_bytes > 0 else 0.0
        
        # Return results
        if total_size_gb > 0:
            return total_size_gb, f"Total size of all weights: {total_size_gb:.2f} GB"
        else:
            error_msg = error_message or "Could not determine model size"
            logger.error(f"Failed to get size for {model_id}: {error_msg}")
            return 0.0, f"Error: {error_msg}"
            
    except Exception as e:
        logger.error(f"Unexpected error when fetching Hugging Face model size: {str(e)}")
        return 0.0, f"Error: Failed to fetch size - {str(e)}"

async def get_model_size_modelscope(model_id: str, token: Optional[str] = None) -> Tuple[float, str]:
    """
    Calculate the total size of all files in a ModelScope model repository.
    Returns size in GB and a status message.
    """
    try:
        if not MS_AVAILABLE:
            return 0.0, "Error: modelscope SDK not installed"
        
        ms_api = HubApi()
        if token:
            try:
                ms_api.login(token)
            except Exception as e:
                logger.error(f"Failed to login to ModelScope: {str(e)}")
                return 0.0, f"Error: Failed to login - {str(e)}"
        
        model_info = None
        files = []
        try:
            # Get model info first
            model_info = ms_api.get_model(model_id)
            logger.info(f"Model info: {model_info}")
            
            # Get model files with detailed info
            files = ms_api.get_model_files(model_id)
            logger.info(f"Model files: {files}")
        except Exception as e:
            logger.error(f"Failed to get model info/files for {model_id}: {str(e)}")
            return 0.0, f"Error: Failed to get model info/files - {str(e)}"
            
        if not files:
            return 0.0, "Error: No files found in model repository"
        
        total_size_bytes = 0
        logger.info(f"Fetching size for ModelScope model: {model_id}")
        
        # Calculate total size from files
        for file in files:
            try:
                if isinstance(file, dict):
                    # Handle file info from get_model_files
                    if 'size' in file and file['size'] is not None:
                        total_size_bytes += file['size']
                    elif 'Size' in file and file['Size'] is not None:
                        total_size_bytes += file['Size']
                    elif 'file_size' in file and file['file_size'] is not None:
                        total_size_bytes += file['file_size']
                elif hasattr(file, 'size') and file.size is not None:
                    total_size_bytes += file.size
                elif hasattr(file, 'Size') and file.Size is not None:
                    total_size_bytes += file.Size
                elif hasattr(file, 'file_size') and file.file_size is not None:
                    total_size_bytes += file.file_size
            except Exception as e:
                logger.warning(f"Failed to get size for file: {str(e)}")
                continue
        
        # If we couldn't get size from files, try to get from model info
        if total_size_bytes == 0 and model_info:
            try:
                if isinstance(model_info, dict):
                    if 'size' in model_info and model_info['size'] is not None:
                        total_size_bytes = model_info['size']
                    elif 'Size' in model_info and model_info['Size'] is not None:
                        total_size_bytes = model_info['Size']
                    elif 'model_size' in model_info and model_info['model_size'] is not None:
                        total_size_bytes = model_info['model_size']
                elif hasattr(model_info, 'size') and model_info.size is not None:
                    total_size_bytes = model_info.size
                elif hasattr(model_info, 'Size') and model_info.Size is not None:
                    total_size_bytes = model_info.Size
                elif hasattr(model_info, 'model_size') and model_info.model_size is not None:
                    total_size_bytes = model_info.model_size
            except Exception as e:
                logger.warning(f"Failed to get size from model info: {str(e)}")
        
        # If still no size, try to get from model version info
        if total_size_bytes == 0:
            try:
                versions = ms_api.list_model_versions(model_id)
                if versions and len(versions) > 0:
                    latest_version = versions[0]
                    if isinstance(latest_version, dict):
                        if 'size' in latest_version and latest_version['size'] is not None:
                            total_size_bytes = latest_version['size']
                        elif 'Size' in latest_version and latest_version['Size'] is not None:
                            total_size_bytes = latest_version['Size']
                        elif 'model_size' in latest_version and latest_version['model_size'] is not None:
                            total_size_bytes = latest_version['model_size']
                    elif hasattr(latest_version, 'size') and latest_version.size is not None:
                        total_size_bytes = latest_version.size
                    elif hasattr(latest_version, 'Size') and latest_version.Size is not None:
                        total_size_bytes = latest_version.Size
                    elif hasattr(latest_version, 'model_size') and latest_version.model_size is not None:
                        total_size_bytes = latest_version.model_size
            except Exception as e:
                logger.warning(f"Failed to get size from model version: {str(e)}")
        
        total_size_gb = total_size_bytes / (1024 ** 3) if total_size_bytes and total_size_bytes > 0 else 0.0
        if total_size_gb == 0.0:
            return 0.0, "Warning: Could not determine model size"
        return total_size_gb, f"Total size of all weights: {total_size_gb:.2f} GB"

    except Exception as e:
        logger.error(f"Error fetching ModelScope model size for {model_id}: {str(e)}")
        return 0.0, f"Error: Failed to fetch size - {str(e)}"

# Helper function to filter files based on regex pattern
def filter_files_by_regex(files: List[str], pattern: str) -> List[str]:
    """
    Filter a list of files using a regex pattern.
    Returns only files that match the pattern.
    """
    try:
        regex = re.compile(pattern)
        return [f for f in files if regex.search(f)]
    except re.error as e:
        logger.error(f"Invalid regex pattern: {e}")
        return files  # Return original files if regex is invalid

def update_task_progress(task_id: str, downloaded_size: int, total_size: int, status: str = None):
    """Helper to update task progress"""
    if task_id in download_tasks:
        if status:
            download_tasks[task_id]['status'] = status
        
        download_tasks[task_id]['downloaded_size'] = downloaded_size
        
        if total_size > 0:
            download_tasks[task_id]['total_size'] = total_size
            progress = min(round((downloaded_size / total_size) * 100), 100)
            download_tasks[task_id]['progress'] = progress
        else:
            download_tasks[task_id]['progress'] = 0

def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get current task status from global store"""
    if task_id not in download_tasks:
        return {
            "task_id": task_id,
            "status": "not_found",
            "error_message": "Task not found"
        }
    return download_tasks[task_id]

def download_huggingface_model_core(task_id: str, model_id: str, save_path: Optional[str], token: Optional[str], 
                                     hf_mirror: Optional[str], file_filter: Optional[str] = None,
                                     archive_after: bool = False, target_drive_path: Optional[str] = None,
                                     archive_name: Optional[str] = None, archive_format: Optional[str] = "zip"):
    if not HF_AVAILABLE:
        update_task_progress(task_id, 0, 0, status="error")
        download_tasks[task_id]['error_message'] = "huggingface_hub SDK not installed"
        return

    actual_save_path = Path(save_path or os.path.join(os.getcwd(), "models", model_id.replace("/", "_")))
    actual_save_path.mkdir(parents=True, exist_ok=True)
    temp_dir = actual_save_path / "tmp" # For partial downloads if snapshot_download doesn't handle resume well for us
    temp_dir.mkdir(parents=True, exist_ok=True)

    download_tasks[task_id].update({
        "status": "downloading",
        "save_path": str(actual_save_path),
        "temp_dir": str(temp_dir)
    })

    original_hf_mirror = os.environ.get("HF_HUB_ENDPOINT")
    if hf_mirror:
        os.environ["HF_HUB_ENDPOINT"] = hf_mirror
        logger.info(f"Task {task_id}: Using Hugging Face mirror: {hf_mirror}")
    
    # Get total size for progress calculation
    # We need a reliable way to get total size of all files to be downloaded
    # snapshot_download doesn't directly give total size before starting
    # Let's try to get it via list_repo_tree again
    total_size = 0
    files_to_download = []
    
    try:
        hf_api_local = HfApi()
        if token: # Authenticate HfApi instance if token is provided
            hf_api_local.token = token
            # Also set global token for snapshot_download if not using HfApi's direct methods for download
            HfFolder.save_token(token)

        # Get the full list of files
        repo_files_info = list(hf_api_local.list_repo_tree(model_id, repo_type="model", token=token, recursive=True))
        
        # Extract file paths
        all_files = [item.path for item in repo_files_info if hasattr(item, 'path') and not item.path.endswith('/')]
        
        # Apply filter if provided
        if file_filter:
            logger.info(f"Task {task_id}: Filtering files with pattern: {file_filter}")
            files_to_download = filter_files_by_regex(all_files, file_filter)
            logger.info(f"Task {task_id}: Selected {len(files_to_download)} of {len(all_files)} files")
            
            if not files_to_download:
                logger.warning(f"Task {task_id}: No files matched the filter pattern!")
                update_task_progress(task_id, 0, 0, status="error")
                download_tasks[task_id]['error_message'] = "No files matched the filter pattern"
                return
        else:
            files_to_download = all_files
            
        # Calculate total size of files to download
        for item in repo_files_info:
            if hasattr(item, 'path') and item.path in files_to_download and hasattr(item, 'size') and item.size is not None:
                total_size += item.size
                
        download_tasks[task_id]['total_size'] = total_size
        download_tasks[task_id]['filtered_files'] = files_to_download
        logger.info(f"Task {task_id}: Calculated total size for {model_id} is {total_size} bytes for {len(files_to_download)} files.")
    except Exception as e:
        logger.error(f"Task {task_id}: Could not determine total size for {model_id} before download: {e}")
        # Continue without total_size, progress will be based on file count or not shown accurately
        download_tasks[task_id]['total_size'] = 0 # Indicate unknown total size

    downloaded_so_far = 0 # This will be tricky with snapshot_download
    
    try:
        # Check for cancellation before starting the potentially long download
        if download_tasks[task_id]['status'] == "cancelled":
            logger.info(f"Task {task_id} for {model_id} was cancelled before download started.")
            return

        logger.info(f"Task {task_id}: Starting snapshot_download for {model_id} to {actual_save_path}")
        
        # Use the file filtering capability of snapshot_download if available
        snapshot_download(
            repo_id=model_id,
            repo_type="model",
            local_dir=str(actual_save_path),
            local_dir_use_symlinks=False, # Usually False for portability
            token=token, # Pass token here as well
            # Apply filter patterns if provided
            allow_patterns=files_to_download if file_filter else None,
            resume_download=True, # HF lib handles some level of resume
            # `progress_callback` for snapshot_download is not available.
        )
        
        # After completion, assume all files are downloaded.
        if download_tasks[task_id]['status'] != "cancelled": # Check again, as it's a long op
            update_task_progress(task_id, total_size, total_size, status="completed")
            download_tasks[task_id]['message'] = f"Model {model_id} downloaded successfully to {actual_save_path}"
            logger.info(f"Task {task_id}: {model_id} download completed.")
            
            # If archiving is requested, start archiving process
            if archive_after and download_tasks[task_id]['status'] == "completed":
                download_tasks[task_id]['status'] = "archiving"
                logger.info(f"Task {task_id}: Starting archiving process")
                try:
                    # Ensure target drive exists
                    target_path = Path(target_drive_path)
                    if not target_path.exists():
                        os.makedirs(target_path, exist_ok=True)
                        
                    # Set archive name
                    final_archive_name = archive_name or model_id.replace("/", "_")
                    
                    # Archive the downloaded model
                    logger.info(f"Task {task_id}: Archiving to {target_path}/{final_archive_name}.{archive_format}")
                    archive_file = shutil.make_archive(
                        base_name=str(target_path / final_archive_name),
                        format=archive_format,
                        root_dir=str(actual_save_path.parent),
                        base_dir=actual_save_path.name
                    )
                    
                    download_tasks[task_id]['status'] = "completed"
                    download_tasks[task_id]['archive_path'] = archive_file
                    download_tasks[task_id]['message'] += f" and archived to {archive_file}"
                    logger.info(f"Task {task_id}: Archiving completed: {archive_file}")
                except Exception as e:
                    logger.error(f"Task {task_id}: Error during archiving: {str(e)}")
                    download_tasks[task_id]['status'] = "completed"  # Download was still successful
                    download_tasks[task_id]['error_message'] = f"Download completed, but archiving failed: {str(e)}"
        else:
            logger.info(f"Task {task_id}: {model_id} download was cancelled during operation.")
    
    except Exception as e:
        if download_tasks[task_id]['status'] != "cancelled":
            logger.error(f"Task {task_id}: Failed to download Hugging Face model {model_id}: {str(e)}")
            download_tasks[task_id]['status'] = "error"
            download_tasks[task_id]['error_message'] = str(e)
    finally:
        if hf_mirror:
            if original_hf_mirror:
                os.environ["HF_HUB_ENDPOINT"] = original_hf_mirror
            else:
                del os.environ["HF_HUB_ENDPOINT"]
        # Clean up global token if set
        if token:
            HfFolder.delete_token()

def download_modelscope_model_core(task_id: str, model_id: str, save_path: Optional[str], token: Optional[str],
                                    file_filter: Optional[str] = None, archive_after: bool = False, 
                                    target_drive_path: Optional[str] = None, archive_name: Optional[str] = None,
                                    archive_format: Optional[str] = "zip"):
    if not MS_AVAILABLE:
        update_task_progress(task_id, 0, 0, status="error")
        download_tasks[task_id]['error_message'] = "modelscope SDK not installed"
        return

    actual_save_path = Path(save_path or os.path.join(os.getcwd(), "models", model_id.replace("/", "_")))
    actual_save_path.mkdir(parents=True, exist_ok=True)
    
    download_tasks[task_id].update({
        "status": "downloading",
        "save_path": str(actual_save_path)
    })

    # Get total size for progress calculation
    total_size = 0
    files_to_download = []
    
    try:
        ms_api_local = HubApi()
        if token: ms_api_local.login(token) # Login HubApi instance if token is provided
        
        # Get the model files list
        all_files = ms_api_local.get_model_files(model_id=model_id, token=token)
        
        # Process and filter files
        file_paths = []
        if isinstance(all_files, list):
            for file in all_files:
                if isinstance(file, dict) and 'path' in file:
                    file_paths.append(file['path'])
                elif hasattr(file, 'path'):
                    file_paths.append(file.path)
        
        # Apply filter if provided
        if file_filter and file_paths:
            logger.info(f"Task {task_id}: Filtering files with pattern: {file_filter}")
            files_to_download = filter_files_by_regex(file_paths, file_filter)
            logger.info(f"Task {task_id}: Selected {len(files_to_download)} of {len(file_paths)} files")
            
            if not files_to_download:
                logger.warning(f"Task {task_id}: No files matched the filter pattern!")
                update_task_progress(task_id, 0, 0, status="error")
                download_tasks[task_id]['error_message'] = "No files matched the filter pattern"
                return
        else:
            files_to_download = file_paths if file_paths else None
        
        # Get model size information
        model_meta = ms_api_local.get_model(model_id=model_id)
        if hasattr(model_meta, 'size') and model_meta.size:
            total_size = model_meta.size
        elif isinstance(model_meta, dict) and model_meta.get('size'):
            total_size = model_meta.get('size')
        
        download_tasks[task_id]['total_size'] = total_size if total_size else 0
        if files_to_download:
            download_tasks[task_id]['filtered_files'] = files_to_download
        logger.info(f"Task {task_id}: Calculated total size for ModelScope {model_id} is {total_size} bytes.")
    except Exception as e:
        logger.error(f"Task {task_id}: Could not determine total size for ModelScope {model_id}: {e}")
        download_tasks[task_id]['total_size'] = 0

    try:
        if download_tasks[task_id]['status'] == "cancelled":
            logger.info(f"Task {task_id} for ModelScope {model_id} was cancelled before download started.")
            return

        logger.info(f"Task {task_id}: Starting ms_snapshot_download for {model_id} to {actual_save_path}")
        
        # Use ModelScope's filtering capabilities if available
        # Different ModelScope versions might have different parameter names
        try:
            # Try with the most common parameter names first
            if files_to_download:
                cache_dir_from_sdk = ms_snapshot_download(
                    model_id=model_id,
                    cache_dir=str(actual_save_path),
                    token=token,
                    revision='master',
                    file_list=files_to_download  # Most likely parameter name
                )
            else:
                cache_dir_from_sdk = ms_snapshot_download(
                    model_id=model_id,
                    cache_dir=str(actual_save_path),
                    token=token,
                    revision='master'
                )
        except TypeError:
            # Fallback to other possible parameter names
            try:
                if files_to_download:
                    cache_dir_from_sdk = ms_snapshot_download(
                        model_id=model_id,
                        cache_dir=str(actual_save_path),
                        token=token,
                        revision='master',
                        files=files_to_download  # Alternative parameter name
                    )
                else:
                    cache_dir_from_sdk = ms_snapshot_download(
                        model_id=model_id,
                        cache_dir=str(actual_save_path),
                        token=token,
                        revision='master'
                    )
            except TypeError:
                # If all attempts fail, use without filtering
                cache_dir_from_sdk = ms_snapshot_download(
                    model_id=model_id,
                    cache_dir=str(actual_save_path),
                    token=token,
                    revision='master'
                )
                # Apply manual filtering after download if needed
                if files_to_download:
                    logger.info(f"Task {task_id}: SDK doesn't support filtering, applying manual filter after download")
                    # We'd need to implement manual filtering here if needed
        
        if download_tasks[task_id]['status'] != "cancelled":
            update_task_progress(task_id, total_size, total_size, status="completed")
            download_tasks[task_id]['message'] = f"ModelScope model {model_id} downloaded successfully to {cache_dir_from_sdk}"
            logger.info(f"Task {task_id}: ModelScope {model_id} download completed to {cache_dir_from_sdk}.")
            
            # If archiving is requested, start archiving process
            if archive_after and download_tasks[task_id]['status'] == "completed":
                download_tasks[task_id]['status'] = "archiving"
                logger.info(f"Task {task_id}: Starting archiving process")
                try:
                    # Ensure target drive exists
                    target_path = Path(target_drive_path)
                    if not target_path.exists():
                        os.makedirs(target_path, exist_ok=True)
                        
                    # Set archive name
                    final_archive_name = archive_name or model_id.replace("/", "_")
                    
                    # Archive the downloaded model
                    actual_model_path = Path(cache_dir_from_sdk)
                    logger.info(f"Task {task_id}: Archiving to {target_path}/{final_archive_name}.{archive_format}")
                    archive_file = shutil.make_archive(
                        base_name=str(target_path / final_archive_name),
                        format=archive_format,
                        root_dir=str(actual_model_path.parent),
                        base_dir=actual_model_path.name
                    )
                    
                    download_tasks[task_id]['status'] = "completed"
                    download_tasks[task_id]['archive_path'] = archive_file
                    download_tasks[task_id]['message'] += f" and archived to {archive_file}"
                    logger.info(f"Task {task_id}: Archiving completed: {archive_file}")
                except Exception as e:
                    logger.error(f"Task {task_id}: Error during archiving: {str(e)}")
                    download_tasks[task_id]['status'] = "completed"  # Download was still successful
                    download_tasks[task_id]['error_message'] = f"Download completed, but archiving failed: {str(e)}"
        else:
            logger.info(f"Task {task_id}: ModelScope {model_id} download was cancelled during operation.")

    except Exception as e:
        if download_tasks[task_id]['status'] != "cancelled":
            logger.error(f"Task {task_id}: Failed to download ModelScope model {model_id}: {str(e)}")
            download_tasks[task_id]['status'] = "error"
            download_tasks[task_id]['error_message'] = str(e)

@app.post("/api/check-size")
async def check_size_endpoint(request: SizeCheckRequest):
    """
    API endpoint to check the total size of a model repository.
    """
    if not request.modelId:
        raise HTTPException(status_code=400, detail="Model ID is required")

    size_gb, message = 0.0, "Unknown error"
    if request.source == 'huggingface':
        size_gb, message = await get_model_size_huggingface(request.modelId, request.authToken)
    elif request.source == 'modelscope':
        size_gb, message = await get_model_size_modelscope(request.modelId, request.authToken)
    else:
        raise HTTPException(status_code=400, detail="Invalid source specified")

    return {"status": "success" if size_gb > 0 else "error", "message": message, "size_gb": size_gb}

@app.post("/api/download/start")
async def start_download_endpoint(request: DownloadTaskRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    download_tasks[task_id] = {
        "task_id": task_id,
        "model_id": request.modelId,
        "source": request.source,
        "status": "pending", # Initial status
        "progress": 0,
        "downloaded_size": 0,
        "total_size": 0, # Will be updated by the download core function
        "save_path_requested": request.savePath,
        "hf_mirror": request.hfMirror,
        "file_filter": request.fileFilter,
        "archive_after": request.archiveAfter,
        "target_drive_path": request.targetDrivePath,
        "archive_name": request.archiveName,
        "archive_format": request.archiveFormat,
        "error_message": None,
        "message": None
    }

    logger.info(f"New download task created: {task_id} for model {request.modelId} from {request.source}")

    if request.source == 'huggingface':
        background_tasks.add_task(download_huggingface_model_core, task_id, request.modelId, 
                                request.savePath, request.authToken, request.hfMirror,
                                request.fileFilter, request.archiveAfter, request.targetDrivePath,
                                request.archiveName, request.archiveFormat)
    elif request.source == 'modelscope':
        background_tasks.add_task(download_modelscope_model_core, task_id, request.modelId, 
                                request.savePath, request.authToken, request.fileFilter,
                                request.archiveAfter, request.targetDrivePath,
                                request.archiveName, request.archiveFormat)
    else:
        download_tasks[task_id]['status'] = "error"
        download_tasks[task_id]['error_message'] = "Invalid source specified"
        raise HTTPException(status_code=400, detail="Invalid source specified")

    return {"task_id": task_id, "status": "pending", "message": "Download task started."}

@app.post("/api/archive")
async def archive_and_move_endpoint(request: ArchiveRequest, background_tasks: BackgroundTasks):
    source_folder = Path(request.sourceFolderPath)
    target_drive = Path(request.targetDrivePath)
    archive_name = request.archiveName or source_folder.name # Default archive name to source folder name
    archive_format = request.archiveFormat or "zip"

    if not source_folder.is_dir():
        raise HTTPException(status_code=400, detail="Source folder path is not a valid directory.")
    if not target_drive.exists(): # Target drive should exist, could be a mount point
        raise HTTPException(status_code=400, detail="Target drive path does not exist.")
    
    # Ensure target is a directory or can be made into one (e.g. root of a drive)
    if target_drive.is_file():
        raise HTTPException(status_code=400, detail="Target drive path points to a file, not a directory.")
    
    target_archive_base = target_drive / archive_name # e.g., /mnt/usb/my_model_archive (no extension yet)
    
    task_id = f"archive_{str(uuid.uuid4())[:8]}"
    download_tasks[task_id] = { # Using download_tasks for simplicity, can be a separate dict
        "task_id": task_id,
        "type": "archiving",
        "status": "pending",
        "source_folder": str(source_folder),
        "target_drive": str(target_drive),
        "archive_name": str(target_archive_base),
        "archive_format": archive_format,
        "progress": 0, # Could be updated if archiving is chunked, but shutil.make_archive is blocking
        "message": None,
        "error_message": None
    }

    background_tasks.add_task(archive_and_move_core, task_id, source_folder, target_drive, archive_name, archive_format)
    
    return {"task_id": task_id, "status": "pending", "message": "Archiving task started."}

def archive_and_move_core(task_id: str, source_folder: Path, target_drive: Path, archive_name_base: str, archive_format: str = "zip"):
    download_tasks[task_id]['status'] = 'processing'
    
    # Output path for the archive file, e.g., /mnt/usb/my_model_archive.zip
    output_archive_path = target_drive / f"{archive_name_base}.{archive_format}"
    
    try:
        logger.info(f"Task {task_id}: Starting archive of {source_folder} to {output_archive_path} using format {archive_format}")
        
        # Create archive in the target_drive directory
        archive_file_created = shutil.make_archive(
            base_name=str(target_drive / archive_name_base), # e.g. /mnt/usb/my_model_archive
            format=archive_format,      # e.g. zip
            root_dir=str(source_folder.parent), # Parent of the dir to archive
            base_dir=source_folder.name # The dir to archive
        )

        logger.info(f"Task {task_id}: Archive created successfully at {archive_file_created}")
        download_tasks[task_id]['status'] = 'completed'
        download_tasks[task_id]['progress'] = 100
        download_tasks[task_id]['message'] = f"Folder {source_folder} archived to {archive_file_created}"

    except Exception as e:
        logger.error(f"Task {task_id}: Failed to archive/move {source_folder}: {str(e)}")
        download_tasks[task_id]['status'] = 'error'
        download_tasks[task_id]['error_message'] = str(e)

@app.get("/api/download/progress/{task_id}")
async def get_download_progress_endpoint(task_id: str):
    task_info = get_task_status(task_id)
    return task_info

@app.post("/api/download/pause/{task_id}")
async def pause_download_endpoint(task_id: str):
    task_info = get_task_status(task_id)
    if task_info['status'] == "downloading":
        # Note: True pause for snapshot_download is not directly supported by SDKs.
        # This is a conceptual pause; the SDK might continue downloading in background.
        # For robust pause, file-by-file download is needed.
        task_info['status'] = "paused_requested" # SDK might not obey immediately
        logger.info(f"Task {task_id} pause requested.")
        return {"task_id": task_id, "status": "paused_requested", "message": "Pause requested. Actual pause depends on SDK."}
    return {"task_id": task_id, "status": task_info['status'], "message": "Task not in downloadable state to pause."}

@app.post("/api/download/resume/{task_id}")
async def resume_download_endpoint(task_id: str):
    task_info = get_task_status(task_id)
    if task_info['status'] == "paused_requested" or task_info['status'] == "paused": # Assuming SDK could set to "paused"
        # Similar to pause, resume depends on SDK's capability.
        task_info['status'] = "downloading" # Request to resume
        logger.info(f"Task {task_id} resume requested.")
        # The background task needs to check this status and act if it was truly paused.
        # With snapshot_download, it might just continue where it left off if resume_download=True was set.
        return {"task_id": task_id, "status": "downloading", "message": "Resume requested."}
    return {"task_id": task_id, "status": task_info['status'], "message": "Task not in pausable state to resume."}

@app.post("/api/download/cancel/{task_id}")
async def cancel_download_endpoint(task_id: str):
    task_info = get_task_status(task_id)
    if task_info['status'] in ["pending", "downloading", "paused_requested", "paused"]:
        task_info['status'] = "cancelled"
        logger.info(f"Task {task_id} cancellation requested.")
        # The core download function needs to check this flag and stop.
        # Cleanup of partial files would happen in the core function's finally block or upon detecting cancellation.
        return {"task_id": task_id, "status": "cancelled", "message": "Cancellation requested."}
    return {"task_id": task_id, "status": task_info['status'], "message": "Task cannot be cancelled or already finished."}

@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "huggingface_available": HF_AVAILABLE,
        "modelscope_available": MS_AVAILABLE
    }

if __name__ == '__main__':
    import uvicorn
    logger.info("Starting Model Downloader Backend...")
    # For development, allow reload
    uvicorn.run("backend:app", host="0.0.0.0", port=5000, reload=True)