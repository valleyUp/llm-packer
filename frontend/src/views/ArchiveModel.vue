<template>
  <div class="archive-model-view">
    <transition name="fade" appear>
      <h2 class="view-title">Archive Model</h2>
    </transition>
    
    <transition name="slide-fade" appear>
      <el-card class="archive-card" :body-style="{ padding: '32px' }">
        <el-form :model="form" label-position="top">
          <div class="form-grid">
            <el-form-item label="Source Folder Path" prop="sourceFolderPath" required class="form-grid-item">
              <el-input 
                v-model="form.sourceFolderPath" 
                size="large"
                placeholder="Path to the downloaded model folder"
                :prefix-icon="FolderOpened"
              ></el-input>
              <div class="form-hint">
                Enter the full path to the folder containing the model files
              </div>
            </el-form-item>
            
            <el-form-item label="Target Drive Path" prop="targetDrivePath" required class="form-grid-item">
              <el-input 
                v-model="form.targetDrivePath" 
                size="large"
                placeholder="Path to your external drive"
                :prefix-icon="HardDisk"
              ></el-input>
              <div class="form-hint">
                Enter the path where the archive should be saved
              </div>
            </el-form-item>
            
            <el-form-item label="Archive Name" prop="archiveName" class="form-grid-item">
              <el-input 
                v-model="form.archiveName" 
                size="large"
                placeholder="e.g., my_model_archive"
                :prefix-icon="Document"
              ></el-input>
              <div class="form-hint">
                Name for the archive file (without extension)
              </div>
            </el-form-item>
            
            <el-form-item label="Archive Format" prop="archiveFormat" class="form-grid-item">
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
          </div>
          
          <div class="form-actions">
            <el-button
              type="primary"
              size="large"
              @click="handleArchive" 
              :loading="isArchiving"
              class="archive-button"
            >
              <el-icon><Box /></el-icon>
              <span>Start Archiving</span>
            </el-button>
          </div>
        </el-form>
      </el-card>
    </transition>
    
    <transition name="scale-fade">
      <el-card v-if="currentTask && currentTask.type === 'archive'" class="task-card" :body-style="{ padding: '24px' }">
        <template #header>
          <div class="task-header">
            <div class="task-title">
              <el-icon class="task-icon"><Box /></el-icon>
              <h3>Archive Progress</h3>
            </div>
            <el-tag :type="taskStatusType" effect="dark" round>{{ currentTask.status }}</el-tag>
          </div>
        </template>
        
        <div class="task-info">
          <div class="task-property">
            <div class="property-label">Source</div>
            <div class="property-value">{{ currentTask.sourcePath }}</div>
          </div>
          
          <div class="task-property">
            <div class="property-label">Target</div>
            <div class="property-value">{{ currentTask.targetPath }}/{{ currentTask.archiveName }}.{{ currentTask.archiveFormat }}</div>
          </div>
        </div>
        
        <div class="progress-section">
          <div class="progress-header">
            <div class="progress-percentage">{{ Math.round(currentTask.progress || 0) }}%</div>
          </div>
          
          <el-progress 
            :percentage="currentTask.progress || 0" 
            :stroke-width="8" 
            :status="taskProgressStatus"
            :show-text="false"
          ></el-progress>
        </div>
      </el-card>
    </transition>
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import { useStore } from 'vuex';
import { ElMessage } from 'element-plus';
import { 
  Box, 
  FolderOpened, 
  HardDisk, 
  Document,
  Compass,
  Collection,
  Connection,
  Histogram,
  Star
} from '@element-plus/icons-vue';

export default {
  name: 'ArchiveModel',
  
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
    
    // 表单数据
    const form = ref({
      sourceFolderPath: '',
      targetDrivePath: '',
      archiveName: 'model_archive',
      archiveFormat: 'zip',
    });
    
    // 状态
    const isArchiving = ref(false);
    
    // 当前任务
    const currentTask = computed(() => store.state.task.currentTask);
    
    // 任务状态类型
    const taskStatusType = computed(() => {
      const status = currentTask.value?.status;
      if (!status) return '';
      
      const statusMap = {
        'created': 'info',
        'archiving': 'primary',
        'completed': 'success',
        'failed': 'danger',
        'cancelled': 'warning',
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
    
    // 开始归档
    const handleArchive = async () => {
      if (!form.value.sourceFolderPath || !form.value.targetDrivePath) {
        ElMessage.warning('Please enter both source folder and target drive paths');
        return;
      }
      
      isArchiving.value = true;
      
      try {
        await store.dispatch('task/archiveModel', {
          sourceFolderPath: form.value.sourceFolderPath,
          targetDrivePath: form.value.targetDrivePath,
          archiveName: form.value.archiveName,
          archiveFormat: form.value.archiveFormat,
        });
        
        ElMessage.success('Archive task started successfully');
      } catch (error) {
        ElMessage.error(`Failed to start archive: ${error.message}`);
      } finally {
        isArchiving.value = false;
      }
    };
    
    return {
      form,
      isArchiving,
      currentTask,
      taskStatusType,
      taskProgressStatus,
      handleArchive,
      archiveFormats,
      // Icons
      Box,
      FolderOpened,
      HardDisk,
      Document,
    };
  },
};
</script>

<style scoped>
.archive-model-view {
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

.archive-card {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  margin-bottom: 2rem;
  transition: all 0.3s ease;
}

.archive-card:hover {
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

.form-hint {
  font-size: 0.85rem;
  color: #909399;
  margin-top: 0.5rem;
  line-height: 1.4;
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

/* Button styles */
.form-actions {
  margin-top: 32px;
  display: flex;
  justify-content: center;
}

.archive-button {
  padding: 12px 32px;
  font-size: 1rem;
  display: flex;
  gap: 8px;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  transition: all 0.2s ease;
}

.archive-button:hover {
  transform: translateY(-2px);
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

/* Responsive adjustments */
@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .format-selector {
    grid-template-columns: 1fr;
  }
}
</style> 