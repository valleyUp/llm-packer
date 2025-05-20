<template>
  <div class="archive-model-view">
    <h2 class="view-title">Archive Model</h2>
    
    <el-card class="archive-card">
      <el-form :model="form" label-width="180px" label-position="left">
        <el-form-item label="Source Folder Path" prop="sourceFolderPath" required>
          <el-input v-model="form.sourceFolderPath" placeholder="Path to the downloaded model folder"></el-input>
          <div class="form-hint">
            Enter the full path to the folder containing the model files
          </div>
        </el-form-item>
        
        <el-form-item label="Target Drive Path" prop="targetDrivePath" required>
          <el-input v-model="form.targetDrivePath" placeholder="Path to your external drive"></el-input>
          <div class="form-hint">
            Enter the path where the archive should be saved
          </div>
        </el-form-item>
        
        <el-form-item label="Archive Name" prop="archiveName">
          <el-input v-model="form.archiveName" placeholder="e.g., my_model_archive"></el-input>
          <div class="form-hint">
            Name for the archive file (without extension)
          </div>
        </el-form-item>
        
        <el-form-item label="Archive Format" prop="archiveFormat">
          <el-select v-model="form.archiveFormat" placeholder="Select format" style="width: 100%;">
            <el-option label="ZIP" value="zip"></el-option>
            <el-option label="TAR" value="tar"></el-option>
            <el-option label="TAR.GZ" value="gztar"></el-option>
            <el-option label="TAR.BZ2" value="bztar"></el-option>
            <el-option label="TAR.XZ" value="xztar"></el-option>
          </el-select>
          <div class="form-hint">
            <strong>ZIP</strong>: Most compatible, <strong>TAR.GZ</strong>: Good compression/speed balance, <strong>TAR.XZ</strong>: Best compression
          </div>
        </el-form-item>
      </el-form>
      
      <div class="form-actions">
        <el-button type="primary" @click="handleArchive" :loading="isArchiving">
          Start Archiving
        </el-button>
      </div>
    </el-card>
    
    <el-card v-if="currentTask && currentTask.type === 'archive'" class="task-card">
      <template #header>
        <div class="task-header">
          <h3>Archive Progress</h3>
          <el-tag :type="taskStatusType">{{ currentTask.status }}</el-tag>
        </div>
      </template>
      
      <div class="task-info">
        <p><strong>Source:</strong> {{ currentTask.sourcePath }}</p>
        <p><strong>Target:</strong> {{ currentTask.targetPath }}/{{ currentTask.archiveName }}.{{ currentTask.archiveFormat }}</p>
      </div>
      
      <el-progress 
        :percentage="currentTask.progress || 0" 
        :stroke-width="20" 
        :status="taskProgressStatus"
      ></el-progress>
    </el-card>
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import { useStore } from 'vuex';
import { ElMessage } from 'element-plus';

export default {
  name: 'ArchiveModel',
  
  setup() {
    const store = useStore();
    
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
    };
  },
};
</script>

<style scoped>
.archive-model-view {
  max-width: 800px;
  margin: 0 auto;
}

.view-title {
  margin-bottom: 1.5rem;
  color: var(--primary-color);
  text-align: center;
}

.archive-card {
  margin-bottom: 2rem;
}

.form-hint {
  font-size: 0.85rem;
  color: #909399;
  margin-top: 0.5rem;
  line-height: 1.4;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
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
</style> 