<template>
  <div class="task-history-view">
    <h2 class="view-title">Task History</h2>
    
    <el-empty v-if="!taskHistory.length" description="No task history yet"></el-empty>
    
    <el-card v-for="task in taskHistory" :key="task.taskId" class="task-card">
      <template #header>
        <div class="task-header">
          <h3>{{ getTaskTitle(task) }}</h3>
          <el-tag :type="getTaskStatusType(task.status)">{{ task.status }}</el-tag>
        </div>
      </template>
      
      <div class="task-info">
        <template v-if="task.type === 'download'">
          <p><strong>Model:</strong> {{ task.source }}/{{ task.modelId }}</p>
          <p v-if="task.savePath"><strong>Save Path:</strong> {{ task.savePath }}</p>
          <p><strong>Progress:</strong> {{ task.progress.toFixed(1) }}%</p>
          <p><strong>Size:</strong> {{ formatBytes(task.downloadedSize) }} / {{ formatBytes(task.totalSize) }}</p>
        </template>
        
        <template v-else-if="task.type === 'archive'">
          <p><strong>Source:</strong> {{ task.sourcePath }}</p>
          <p><strong>Target:</strong> {{ task.targetPath }}/{{ task.archiveName }}.{{ task.archiveFormat }}</p>
          <p><strong>Progress:</strong> {{ task.progress.toFixed(1) }}%</p>
        </template>
      </div>
      
      <div class="task-time">
        <p v-if="task.startTime">
          <strong>Started:</strong> {{ formatTime(task.startTime) }}
        </p>
        <p v-if="task.lastUpdateTime && task.status === 'completed'">
          <strong>Completed:</strong> {{ formatTime(task.lastUpdateTime) }}
        </p>
      </div>
    </el-card>
  </div>
</template>

<script>
import { computed } from 'vue';
import { useStore } from 'vuex';

export default {
  name: 'TaskHistory',
  
  setup() {
    const store = useStore();
    
    // 获取任务历史
    const taskHistory = computed(() => store.state.task.taskHistory);
    
    // 获取任务标题
    const getTaskTitle = (task) => {
      if (task.type === 'download') {
        return `Download: ${task.modelId.split('/').pop()}`;
      } else if (task.type === 'archive') {
        return `Archive: ${task.archiveName}`;
      }
      return `Task ${task.taskId}`;
    };
    
    // 获取任务状态类型
    const getTaskStatusType = (status) => {
      const statusMap = {
        'created': 'info',
        'downloading': 'primary',
        'archiving': 'primary',
        'completed': 'success',
        'failed': 'danger',
        'cancelled': 'warning',
      };
      
      return statusMap[status] || 'info';
    };
    
    // 格式化字节
    const formatBytes = (bytes, decimals = 2) => {
      if (!bytes || bytes === 0) return '0 Bytes';
      
      const k = 1024;
      const dm = decimals < 0 ? 0 : decimals;
      const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB'];
      
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      
      return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    };
    
    // 格式化时间
    const formatTime = (timestamp) => {
      if (!timestamp) return '';
      
      const date = new Date(timestamp * 1000);
      return date.toLocaleString();
    };
    
    return {
      taskHistory,
      getTaskTitle,
      getTaskStatusType,
      formatBytes,
      formatTime,
    };
  },
};
</script>

<style scoped>
.task-history-view {
  max-width: 800px;
  margin: 0 auto;
}

.view-title {
  margin-bottom: 1.5rem;
  color: var(--primary-color);
  text-align: center;
}

.task-card {
  margin-bottom: 1.5rem;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-info {
  margin-bottom: 1rem;
}

.task-info p {
  margin-bottom: 0.5rem;
}

.task-time {
  font-size: 0.9rem;
  color: #909399;
  border-top: 1px solid var(--border-color);
  padding-top: 0.75rem;
  margin-top: 0.75rem;
}

.task-time p {
  margin-bottom: 0.25rem;
}
</style> 