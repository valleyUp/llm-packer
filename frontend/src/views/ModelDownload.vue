<template>
  <div class="model-download-view">
    <h2 class="view-title">Download Model Weights</h2>
    
    <el-card class="download-card">
      <el-form :model="form" label-width="180px" label-position="left">
        <el-form-item label="Model Source" prop="source">
          <el-select v-model="form.source" placeholder="Select source" style="width: 100%;">
            <el-option label="ModelScope" value="modelscope"></el-option>
            <el-option label="Hugging Face" value="huggingface"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="Model ID/URL" prop="modelId">
          <el-input v-model="form.modelId" placeholder="Enter Model ID or URL"></el-input>
          <div class="form-hint">
            <el-skeleton v-if="isCheckingSize" :rows="1" animated />
            <template v-else-if="store.state.model.modelSizeInfo">
              <div class="model-size-info-container">
                <el-alert
                  :type="modelSizeAlertType"
                  :title="modelSizeDisplay"
                  show-icon
                  :closable="false"
                />
              </div>
            </template>
          </div>
        </el-form-item>
        
        <el-form-item label="Authentication Token" prop="authToken">
          <el-input type="password" v-model="form.authToken" show-password placeholder="Enter API Token"></el-input>
        </el-form-item>
        
        <el-form-item v-if="form.source === 'huggingface'" label="HF Mirror URL" prop="hfMirror">
          <el-input v-model="form.hfMirror" placeholder="Enter Hugging Face Mirror URL"></el-input>
        </el-form-item>
        
        <el-form-item label="Save Path" prop="savePath">
          <el-input v-model="form.savePath" placeholder="Default: ./models/[model_id]"></el-input>
        </el-form-item>
        
        <el-form-item label="Filter Files" prop="fileFilter">
          <el-input v-model="form.fileFilter" placeholder="Regex pattern to filter files (e.g., .*\.safetensors)"></el-input>
          <div class="form-hint">
            Use regex patterns to filter which files to download.<br>
            Examples: <code>.*\.safetensors</code> (only safetensors files), <code>.*\.(bin|pt)</code> (bin or pt files)
          </div>
        </el-form-item>
        
        <el-divider>Archive Options</el-divider>
        
        <el-form-item label="Archive After Download" prop="archiveAfter">
          <el-switch v-model="form.archiveAfter"></el-switch>
        </el-form-item>
        
        <template v-if="form.archiveAfter">
          <el-form-item label="Target Drive Path" prop="targetDrivePath">
            <el-input v-model="form.targetDrivePath" placeholder="Path to your external drive"></el-input>
          </el-form-item>
          
          <el-form-item label="Archive Name" prop="archiveName">
            <el-input v-model="form.archiveName" placeholder="e.g., my_model_archive"></el-input>
          </el-form-item>
          
          <el-form-item label="Archive Format" prop="archiveFormat">
            <el-select v-model="form.archiveFormat" placeholder="Select format" style="width: 100%;">
              <el-option label="ZIP" value="zip"></el-option>
              <el-option label="TAR" value="tar"></el-option>
              <el-option label="TAR.GZ" value="gztar"></el-option>
              <el-option label="TAR.BZ2" value="bztar"></el-option>
              <el-option label="TAR.XZ" value="xztar"></el-option>
            </el-select>
          </el-form-item>
          
          <el-form-item label=" " v-if="compressedSizeEstimate">
            <div class="model-size-info-container">
              <el-alert
                type="info"
                :title="`Estimated compressed size: ${compressedSizeEstimate}`"
                show-icon
                :closable="false"
              />
            </div>
          </el-form-item>
        </template>
      </el-form>
      
      <div class="form-actions">
        <el-button @click="handleCheckSize" :loading="isCheckingSize">
          Check Size
        </el-button>
        <el-button type="primary" @click="handleStartDownload" :loading="isStartingDownload">
          Start Download
        </el-button>
      </div>
    </el-card>
    
    <el-card v-if="currentTask" class="task-card">
      <template #header>
        <div class="task-header">
          <h3>Download Progress</h3>
          <el-tag :type="taskStatusType">{{ currentTask.status }}</el-tag>
        </div>
      </template>
      
      <div class="task-info">
        <p><strong>Model:</strong> {{ currentTask.source }}/{{ currentTask.modelId }}</p>
        <p v-if="currentTask.savePath"><strong>Save Path:</strong> {{ currentTask.savePath }}</p>
      </div>
      
      <el-progress 
        :percentage="currentTask.progress || 0" 
        :stroke-width="20" 
        :status="taskProgressStatus"
      ></el-progress>
      
      <div class="task-details">
        <p v-if="currentTask.downloadedSize && currentTask.totalSize">
          {{ formatBytes(currentTask.downloadedSize) }} / {{ formatBytes(currentTask.totalSize) }}
        </p>
        <p v-if="formattedSpeed">Speed: {{ formattedSpeed }}</p>
        <p v-if="currentTask.estimatedTimeLeft">Time left: {{ currentTask.estimatedTimeLeft }}</p>
      </div>
      
      <div class="task-actions">
        <el-button @click="handleCancelDownload" type="danger">Cancel</el-button>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, computed, onUnmounted } from 'vue';
import { useStore } from 'vuex';
import { ElMessage } from 'element-plus';

export default {
  name: 'ModelDownload',
  
  setup() {
    const store = useStore();
    
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
      const sizeFormatted = store.getters['model/modelSizeFormatted'];
      const modelInfo = store.state.model.modelSizeInfo;
      
      console.log('Computing modelSizeDisplay:', { 
        sizeFormatted, 
        modelInfo,
        source: form.value.source
      });
      
      // 直接检查模型信息和大小值
      if (modelInfo && modelInfo.sizeGB) {
        const sizeGB = parseFloat(modelInfo.sizeGB);
        if (!isNaN(sizeGB) && sizeGB > 0) {
          return `Model size: ${sizeGB.toFixed(2)} GB`;
        }
      }
      
      // 如果上述处理失败，回退到使用getter
      if (sizeFormatted) {
        return `Model size: ${sizeFormatted.replace(' GB', '')} GB`;
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
      if (size > 50) return 'warning'; // 大模型警告
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
    };
  },
};
</script>

<style scoped>
.model-download-view {
  max-width: 800px;
  margin: 0 auto;
}

.view-title {
  margin-bottom: 1.5rem;
  color: var(--primary-color);
  text-align: center;
}

.download-card {
  margin-bottom: 2rem;
}

.form-hint {
  font-size: 0.85rem;
  color: #909399;
  margin-top: 0.5rem;
  line-height: 1.4;
}

/* 模型大小信息容器样式 */
.model-size-info-container {
  margin-top: 12px;
  margin-bottom: 12px;
}

/* 自定义Alert样式 */
.model-size-info-container :deep(.el-alert) {
  border-radius: 4px;
  font-weight: 500;
}

.model-size-info-container :deep(.el-alert__title) {
  font-size: 14px;
  display: flex;
  align-items: center;
}

.model-size-info-container :deep(.el-alert__icon) {
  font-size: 16px;
  margin-right: 8px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.task-card {
  margin-bottom: 2rem;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-info {
  margin-bottom: 1rem;
}

.task-details {
  margin-top: 1rem;
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  font-size: 0.9rem;
}

.task-actions {
  margin-top: 1.5rem;
  display: flex;
  justify-content: flex-end;
}
</style> 