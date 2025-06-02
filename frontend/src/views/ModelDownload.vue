<template>
  <div class="model-download-view">
    <transition name="fade" appear>
      <h2 class="view-title">Download Model Weights</h2>
    </transition>
    
    <transition name="slide-fade" appear>
      <el-card class="download-card" :body-style="{ padding: '32px' }">
        <el-form :model="form" label-position="top">
          <div class="form-grid">
            <el-form-item label="Model Source" prop="source" class="form-grid-item">
              <div class="source-selector">
                <div 
                  class="source-option" 
                  :class="{ active: form.source === 'huggingface' }" 
                  @click="form.source = 'huggingface'"
                >
                  <div class="source-icon">
                    <svg viewBox="0 0 95 95" xmlns="http://www.w3.org/2000/svg">
                      <path d="M47.5 95C73.71 95 95 73.71 95 47.5S73.71 0 47.5 0 0 21.29 0 47.5 21.29 95 47.5 95z" fill="currentColor" opacity=".2"/>
                      <path d="M29.58 67.45c2.73 0 5.48-.56 7.74-1.71l.28-.14V44.4l-.49-.27a13.38 13.38 0 0 0-6.32-1.59c-7.62 0-12.18 5.82-12.18 12.73 0 7.73 5.31 12.18 10.97 12.18z M54.5 24.06c-6.79 0-12.25 5.24-12.25 11.76 0 6.45 5.46 11.69 12.25 11.69s12.16-5.24 12.16-11.69c0-6.52-5.37-11.76-12.16-11.76z M72.09 42.54a13.43 13.43 0 0 0-6.4 1.59l-.42.21v21.2l.28.14a14.22 14.22 0 0 0 7.74 1.77c5.79 0 10.96-4.45 10.96-12.18 0-6.97-4.23-12.73-12.16-12.73z" fill="currentColor"/>
                    </svg>
                  </div>
                  <span>Hugging Face</span>
                </div>
                
                <div 
                  class="source-option" 
                  :class="{ active: form.source === 'modelscope' }" 
                  @click="form.source = 'modelscope'"
                >
                  <div class="source-icon">
                    <svg viewBox="0 0 95 95" xmlns="http://www.w3.org/2000/svg">
                      <path d="M47.5 95C73.71 95 95 73.71 95 47.5S73.71 0 47.5 0 0 21.29 0 47.5 21.29 95 47.5 95z" fill="currentColor" opacity=".2"/>
                      <path d="M28.58 31.45 47.5 20.27l18.92 11.18v22.37L47.5 65l-18.92-11.18V31.45z M25 28.5v25l22 13 22-13v-25l-22-13-22 13z" fill="currentColor"/>
                    </svg>
                  </div>
                  <span>ModelScope</span>
                </div>
              </div>
            </el-form-item>
            
            <el-form-item label="Model ID/URL" prop="modelId" class="form-grid-item">
              <el-input 
                v-model="form.modelId" 
                placeholder="Enter Model ID or URL"
                size="large"
                :prefix-icon="Document"
              >
                <template #append>
                  <el-button @click="handleCheckSize" :loading="isCheckingSize">
                    Check Size
                  </el-button>
                </template>
              </el-input>
              
              <transition name="fade">
                <div class="model-size-info-container" v-if="store.state.model.modelSizeInfo || isCheckingSize">
                  <el-skeleton v-if="isCheckingSize" :rows="1" animated />
                  <el-alert
                    v-else
                    :type="modelSizeAlertType"
                    :title="modelSizeDisplay"
                    show-icon
                    :closable="false"
                  />
                </div>
              </transition>
            </el-form-item>
            
            <el-form-item label="Authentication Token" prop="authToken" class="form-grid-item">
              <el-input 
                type="password" 
                v-model="form.authToken" 
                show-password 
                size="large"
                placeholder="Enter API Token"
                :prefix-icon="Key"
              ></el-input>
            </el-form-item>
            
            <el-form-item v-if="form.source === 'huggingface'" label="HF Mirror URL" prop="hfMirror" class="form-grid-item">
              <el-input 
                v-model="form.hfMirror" 
                size="large"
                placeholder="Enter Hugging Face Mirror URL"
                :prefix-icon="Link"
              ></el-input>
            </el-form-item>
            
            <el-form-item label="Save Path" prop="savePath" class="form-grid-item">
              <el-input 
                v-model="form.savePath" 
                size="large"
                placeholder="Default: ./models/[model_id]"
                :prefix-icon="Folder"
              ></el-input>
            </el-form-item>
            
            <el-form-item label="Filter Files" prop="fileFilter" class="form-grid-item">
              <el-input 
                v-model="form.fileFilter" 
                size="large"
                placeholder="Regex pattern to filter files"
                :prefix-icon="Filter"
              ></el-input>
              <div class="form-hint">
                Examples: <code>.*\.safetensors</code> (only safetensors), <code>.*\.(bin|pt)</code> (bin or pt files)
              </div>
            </el-form-item>
          </div>
          
          <div class="archive-section">
            <el-divider>
              <div class="divider-content">
                <el-icon><Box /></el-icon>
                <span>Archive Options</span>
              </div>
            </el-divider>
            
            <div class="archive-toggle">
              <span>Archive After Download</span>
              <el-switch v-model="form.archiveAfter"></el-switch>
            </div>
            
            <transition name="expand">
              <div class="archive-options" v-if="form.archiveAfter">
                <div class="form-grid">
                  <el-form-item label="Target Drive Path" prop="targetDrivePath" class="form-grid-item">
                    <el-input 
                      v-model="form.targetDrivePath" 
                      size="large"
                      placeholder="Path to your external drive"
                      :prefix-icon="HardDisk"
                    ></el-input>
                  </el-form-item>
                  
                  <el-form-item label="Archive Name" prop="archiveName" class="form-grid-item">
                    <el-input 
                      v-model="form.archiveName" 
                      size="large"
                      placeholder="e.g., my_model_archive"
                      :prefix-icon="Tag"
                    ></el-input>
                  </el-form-item>
                </div>
                
                <el-form-item label="Archive Format" prop="archiveFormat">
                  <div class="format-selector">
                    <div 
                      v-for="format in archiveFormats" 
                      :key="format.value"
                      class="format-option"
                      :class="{ active: form.archiveFormat === format.value }"
                      @click="form.archiveFormat = format.value"
                    >
                      <div class="format-icon">
                        <el-icon><component :is="format.icon" /></el-icon>
                      </div>
                      <div class="format-info">
                        <div class="format-name">{{ format.label }}</div>
                        <div class="format-desc">{{ format.description }}</div>
                      </div>
                    </div>
                  </div>
                </el-form-item>
                
                <transition name="fade">
                  <div class="compressed-size" v-if="compressedSizeEstimate">
                    <el-alert
                      type="info"
                      :title="`Estimated compressed size: ${compressedSizeEstimate}`"
                      show-icon
                      :closable="false"
                    />
                  </div>
                </transition>
              </div>
            </transition>
          </div>
          
          <div class="form-actions">
            <el-button
              type="primary"
              size="large"
              :loading="isStartingDownload"
              @click="handleStartDownload"
              class="download-button"
            >
              <el-icon><Download /></el-icon>
              <span>Start Download</span>
            </el-button>
          </div>
        </el-form>
      </el-card>
    </transition>
    
    <transition name="scale-fade">
      <el-card v-if="currentTask" class="task-card" :body-style="{ padding: '24px' }">
        <template #header>
          <div class="task-header">
            <div class="task-title">
              <el-icon class="task-icon"><Download /></el-icon>
              <h3>Download Progress</h3>
            </div>
            <el-tag :type="taskStatusType" effect="dark" round>{{ currentTask.status }}</el-tag>
          </div>
        </template>
        
        <div class="task-info">
          <div class="task-property">
            <div class="property-label">Model</div>
            <div class="property-value">{{ currentTask.source }}/{{ currentTask.modelId }}</div>
          </div>
          
          <div class="task-property" v-if="currentTask.savePath">
            <div class="property-label">Save Path</div>
            <div class="property-value">{{ currentTask.savePath }}</div>
          </div>
        </div>
        
        <div class="progress-section">
          <div class="progress-header">
            <div class="progress-percentage">{{ Math.round(currentTask.progress || 0) }}%</div>
            <div class="progress-stats" v-if="currentTask.downloadedSize && currentTask.totalSize">
              {{ formatBytes(currentTask.downloadedSize) }} / {{ formatBytes(currentTask.totalSize) }}
            </div>
          </div>
          
          <el-progress 
            :percentage="currentTask.progress || 0" 
            :stroke-width="8" 
            :status="taskProgressStatus"
            :show-text="false"
          ></el-progress>
          
          <div class="task-details">
            <div class="detail-item" v-if="formattedSpeed">
              <el-icon><CaretRight /></el-icon>
              <span>{{ formattedSpeed }}</span>
            </div>
            <div class="detail-item" v-if="currentTask.estimatedTimeLeft">
              <el-icon><Timer /></el-icon>
              <span>{{ currentTask.estimatedTimeLeft }}</span>
            </div>
          </div>
        </div>
        
        <div class="task-actions">
          <el-button 
            @click="handleCancelDownload" 
            type="danger" 
            plain
            size="large"
            :icon="CircleClose"
          >
            Cancel Download
          </el-button>
        </div>
      </el-card>
    </transition>
  </div>
</template>

<script>
import { ref, computed, onUnmounted } from 'vue';
import { useStore } from 'vuex';
import { ElMessage } from 'element-plus';
import { 
  Download, 
  Document, 
  Key, 
  Folder, 
  Filter, 
  Link, 
  Box, 
  HardDisk, 
  Tag,
  Timer,
  CaretRight,
  CircleClose,
  Histogram,
  Connection,
  Compass,
  Collection,
  Star
} from '@element-plus/icons-vue';

export default {
  name: 'ModelDownload',
  
  setup() {
    const store = useStore();
    
    // Archive format options
    const archiveFormats = [
      { 
        label: 'ZIP', 
        value: 'zip',
        icon: Compass,
        description: 'Most compatible format'
      },
      { 
        label: 'TAR', 
        value: 'tar',
        icon: Collection,
        description: 'Unix tape archive (no compression)'
      },
      { 
        label: 'TAR.GZ', 
        value: 'gztar',
        icon: Connection,
        description: 'Good balance of speed and size'
      },
      { 
        label: 'TAR.BZ2', 
        value: 'bztar',
        icon: Histogram,
        description: 'Better compression than gzip'
      },
      { 
        label: 'TAR.XZ', 
        value: 'xztar',
        icon: Star,
        description: 'Best compression but slowest'
      }
    ];
    
    // 开发模式标志
    const isDev = process.env.NODE_ENV === 'development';
    
    // 表单数据
    const form = ref({
      source: 'huggingface',
      modelId: '',
      authToken: '',
      hfMirror: '',
      savePath: '',
      fileFilter: '',
      archiveAfter: false,
      targetDrivePath: '',
      archiveName: '',
      archiveFormat: 'zip',
    });
    
    // 状态
    const isCheckingSize = computed(() => store.state.model.isCheckingSize);
    const isStartingDownload = ref(false);
    
    // 模型大小信息展示相关
    const modelSizeInfo = computed(() => {
      const sizeFormatted = store.getters['model/modelSizeFormatted'];
      const sizeMessage = store.getters['model/modelSizeMessage'];
      
      if (sizeFormatted) {
        return `Model size: ${sizeFormatted} - ${sizeMessage}`;
      }
      return '';
    });
    
    // 简化后的模型大小显示
    const modelSizeDisplay = computed(() => {
      const modelInfo = store.state.model.modelSizeInfo;
      
      // 如果有模型信息，直接展示
      if (modelInfo) {
        let sizeValue;
        
        // 尝试多种方式获取大小值
        try {
          // 先尝试直接获取数值
          sizeValue = Number(modelInfo.sizeGB);
          
          // 如果是NaN，可能是字符串需要解析
          if (isNaN(sizeValue) && typeof modelInfo.sizeGB === 'string') {
            // 可能是JSON字符串
            try {
              const parsed = JSON.parse(modelInfo.sizeGB);
              sizeValue = Number(parsed);
            } catch (e) {
              // 解析失败，跳过
            }
          }
          
          // 如果有有效值，直接显示
          if (!isNaN(sizeValue) && sizeValue > 0) {
            return `Model size: ${sizeValue.toFixed(2)} GB`;
          }
        } catch (e) {
          // 静默处理错误
        }
      }
      
      // 错误处理
      if (modelInfo && modelInfo.message && modelInfo.message.toLowerCase().includes('error')) {
        return `Error: Unable to determine model size`;
      }
      
      return 'Model size unavailable';
    });
    
    const modelSizeAlertType = computed(() => {
      const modelInfo = store.state.model.modelSizeInfo;
      if (!modelInfo) return 'info';
      
      // 如果是错误消息，使用警告色
      if (modelInfo.message && modelInfo.message.toLowerCase().includes('error')) {
        return 'warning';
      }
      
      // 根据模型大小判断提示类型
      const size = modelInfo.sizeGB || 0;
      if (size === 0) return 'warning';
      if (size > 50) return 'success'; // 大模型使用成功色
      if (size > 10) return 'info';
      return 'success';
    });
    
    const modelSizeTitle = computed(() => {
      const sizeFormatted = store.getters['model/modelSizeFormatted'];
      if (!sizeFormatted) {
        return 'Model size unavailable';
      }
      return `Model size: ${sizeFormatted}`;
    });
    
    const modelSizeDescription = computed(() => {
      return store.getters['model/modelSizeMessage'] || '';
    });
    
    // 压缩大小估计
    const compressedSizeEstimate = computed(() => store.getters['model/compressedSizeEstimate']);
    
    // 当前任务
    const currentTask = computed(() => store.state.task.currentTask);
    
    // 任务状态类型
    const taskStatusType = computed(() => {
      const status = currentTask.value?.status;
      if (!status) return '';
      
      const statusMap = {
        'created': 'info',
        'downloading': 'primary',
        'completed': 'success',
        'failed': 'danger',
        'cancelled': 'warning',
        'archiving': 'warning',
      };
      
      return statusMap[status] || 'info';
    });
    
    // 任务进度状态
    const taskProgressStatus = computed(() => {
      const status = currentTask.value?.status;
      if (!status) return '';
      
      if (status === 'completed') return 'success';
      if (status === 'failed') return 'exception';
      if (status === 'cancelled') return 'warning';
      
      return '';
    });
    
    // 格式化速度
    const formattedSpeed = computed(() => store.getters['task/formattedSpeed']);
    
    // 检查模型大小
    const handleCheckSize = async () => {
      if (!form.value.source || !form.value.modelId) {
        ElMessage.warning('Please select a source and enter a model ID');
        return;
      }
      
      try {
        await store.dispatch('model/checkModelSize', {
          source: form.value.source,
          modelId: form.value.modelId,
          authToken: form.value.authToken || undefined,
        });
      } catch (error) {
        ElMessage.error(`Failed to check model size: ${error.message}`);
      }
    };
    
    // 开始下载
    const handleStartDownload = async () => {
      if (!form.value.source || !form.value.modelId) {
        ElMessage.warning('Please select a source and enter a model ID');
        return;
      }
      
      isStartingDownload.value = true;
      
      try {
        await store.dispatch('task/startDownload', {
          ...form.value,
          authToken: form.value.authToken || undefined,
          savePath: form.value.savePath || undefined,
          hfMirror: form.value.hfMirror || undefined,
          fileFilter: form.value.fileFilter || undefined,
          archiveName: form.value.archiveName || undefined,
        });
        
        ElMessage.success('Download started successfully');
      } catch (error) {
        ElMessage.error(`Failed to start download: ${error.message}`);
      } finally {
        isStartingDownload.value = false;
      }
    };
    
    // 取消下载
    const handleCancelDownload = async () => {
      if (!currentTask.value) return;
      
      try {
        await store.dispatch('task/cancelTask', currentTask.value.taskId);
        ElMessage.info('Download cancelled');
      } catch (error) {
        ElMessage.error(`Failed to cancel download: ${error.message}`);
      }
    };
    
    // 格式化字节
    const formatBytes = (bytes, decimals = 2) => {
      if (bytes === 0) return '0 Bytes';
      
      const k = 1024;
      const dm = decimals < 0 ? 0 : decimals;
      const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB'];
      
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      
      return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    };
    
    // 组件卸载时清理
    onUnmounted(() => {
      store.dispatch('task/stopPolling');
    });
    
    return {
      form,
      isCheckingSize,
      isStartingDownload,
      modelSizeInfo,
      modelSizeDisplay,
      modelSizeAlertType,
      modelSizeTitle,
      modelSizeDescription,
      compressedSizeEstimate,
      currentTask,
      taskStatusType,
      taskProgressStatus,
      formattedSpeed,
      handleCheckSize,
      handleStartDownload,
      handleCancelDownload,
      formatBytes,
      store,
      isDev,
      archiveFormats,
      // Icons
      Download,
      Document,
      Key,
      Folder,
      Filter,
      Link,
      Box,
      HardDisk,
      Tag,
      Timer,
      CaretRight,
      CircleClose,
    };
  },
};
</script>

<style scoped>
.model-download-view {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 16px;
}

.view-title {
  margin-bottom: 1.5rem;
  color: var(--primary-color);
  text-align: center;
  font-size: 2rem;
  font-weight: 600;
  letter-spacing: -0.01em;
}

.download-card {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  margin-bottom: 2rem;
  transition: all 0.3s ease;
}

.download-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
}

.task-card {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  margin-bottom: 2rem;
  transition: all 0.3s ease;
}

/* Source selector styling */
.source-selector {
  display: flex;
  gap: 16px;
  width: 100%;
}

.source-option {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 16px;
  border-radius: 12px;
  border: 2px solid var(--border-color);
  cursor: pointer;
  transition: all 0.2s ease;
}

.source-option:hover {
  background-color: rgba(var(--el-color-primary-rgb), 0.05);
}

.source-option.active {
  border-color: var(--primary-color);
  background-color: rgba(var(--el-color-primary-rgb), 0.1);
}

.source-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  color: var(--primary-color);
}

.source-icon svg {
  width: 100%;
  height: 100%;
}

.source-option span {
  font-weight: 500;
}

/* Form grid layout */
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
}

.form-grid-item {
  width: 100%;
}

/* Archive section styles */
.archive-section {
  margin-top: 32px;
}

.divider-content {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--primary-color);
  font-weight: 500;
}

.archive-toggle {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
}

.archive-options {
  margin-top: 16px;
}

/* Format selector styles */
.format-selector {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
}

.format-option {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  border-radius: 10px;
  border: 2px solid var(--border-color);
  cursor: pointer;
  transition: all 0.2s ease;
}

.format-option:hover {
  background-color: rgba(var(--el-color-primary-rgb), 0.05);
}

.format-option.active {
  border-color: var(--primary-color);
  background-color: rgba(var(--el-color-primary-rgb), 0.1);
}

.format-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: rgba(var(--el-color-primary-rgb), 0.1);
  color: var(--primary-color);
  margin-right: 12px;
  flex-shrink: 0;
}

.format-info {
  flex: 1;
}

.format-name {
  font-weight: 600;
  margin-bottom: 4px;
}

.format-desc {
  font-size: 0.8rem;
  color: var(--el-text-color-secondary);
}

.form-hint {
  font-size: 0.85rem;
  color: #909399;
  margin-top: 0.5rem;
  line-height: 1.4;
}

/* Model size info container */
.model-size-info-container {
  margin-top: 12px;
}

.model-size-info-container :deep(.el-alert) {
  border-radius: 8px;
}

/* Progress section */
.progress-section {
  padding: 16px 0;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.progress-percentage {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--el-color-primary);
}

.progress-stats {
  font-size: 1rem;
  font-weight: 500;
}

/* Task styles */
.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.task-icon {
  font-size: 20px;
  color: var(--primary-color);
}

.task-info {
  margin-bottom: 24px;
}

.task-property {
  margin-bottom: 12px;
}

.property-label {
  font-size: 0.85rem;
  color: var(--el-text-color-secondary);
  margin-bottom: 4px;
}

.property-value {
  font-weight: 500;
  word-break: break-all;
}

.task-details {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
  margin-top: 16px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--el-text-color-secondary);
}

.task-actions {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

/* Button styles */
.form-actions {
  margin-top: 32px;
  display: flex;
  justify-content: center;
}

.download-button {
  padding: 12px 32px;
  font-size: 1rem;
  display: flex;
  gap: 8px;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  transition: all 0.2s ease;
}

.download-button:hover {
  transform: translateY(-2px);
}

.compressed-size {
  margin-top: 16px;
}

/* Animation classes */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.3s ease-in;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

.scale-fade-enter-active {
  transition: all 0.4s ease-out;
}

.scale-fade-leave-active {
  transition: all 0.4s ease-in;
}

.scale-fade-enter-from,
.scale-fade-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  height: 0;
  opacity: 0;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .source-selector {
    flex-direction: column;
  }
  
  .format-selector {
    grid-template-columns: 1fr;
  }
}
</style> 