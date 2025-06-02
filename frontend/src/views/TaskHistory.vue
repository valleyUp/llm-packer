<template>
  <div class="task-history-view">
    <transition name="fade" appear>
      <h2 class="view-title">Task History</h2>
    </transition>
    
    <transition name="slide-fade" appear>
      <el-empty 
        v-if="!taskHistory.length" 
        description="No task history yet"
        :image-size="200"
      >
        <template #image>
          <el-icon class="empty-icon"><DocumentCopy /></el-icon>
        </template>
      </el-empty>
      
      <div v-else class="history-grid">
        <transition-group name="list" tag="div" class="history-list">
          <el-card 
            v-for="task in taskHistory" 
            :key="task.taskId" 
            class="task-card"
            :body-style="{ padding: '24px' }"
          >
            <template #header>
              <div class="task-header">
                <div class="task-title">
                  <el-icon class="task-icon">
                    <component :is="getTaskIcon(task)"></component>
                  </el-icon>
                  <h3>{{ getTaskTitle(task) }}</h3>
                </div>
                <el-tag :type="getTaskStatusType(task.status)" effect="dark" round>{{ task.status }}</el-tag>
              </div>
            </template>
            
            <div class="task-content">
              <template v-if="task.type === 'download'">
                <div class="task-property">
                  <div class="property-label">Model</div>
                  <div class="property-value">{{ task.source }}/{{ task.modelId }}</div>
                </div>
                
                <div v-if="task.savePath" class="task-property">
                  <div class="property-label">Save Path</div>
                  <div class="property-value">{{ task.savePath }}</div>
                </div>
                
                <div class="task-stats">
                  <div class="stat-item">
                    <div class="stat-value">{{ task.progress.toFixed(1) }}%</div>
                    <div class="stat-label">Progress</div>
                  </div>
                  
                  <div class="stat-item">
                    <div class="stat-value">{{ formatBytes(task.downloadedSize) }}</div>
                    <div class="stat-label">Downloaded</div>
                  </div>
                  
                  <div class="stat-item">
                    <div class="stat-value">{{ formatBytes(task.totalSize) }}</div>
                    <div class="stat-label">Total Size</div>
                  </div>
                </div>
              </template>
              
              <template v-else-if="task.type === 'archive'">
                <div class="task-property">
                  <div class="property-label">Source</div>
                  <div class="property-value">{{ task.sourcePath }}</div>
                </div>
                
                <div class="task-property">
                  <div class="property-label">Target</div>
                  <div class="property-value">{{ task.targetPath }}/{{ task.archiveName }}.{{ task.archiveFormat }}</div>
                </div>
                
                <div class="task-stats">
                  <div class="stat-item">
                    <div class="stat-value">{{ task.progress.toFixed(1) }}%</div>
                    <div class="stat-label">Progress</div>
                  </div>
                </div>
              </template>
              
              <div class="task-timeline">
                <div class="timeline-item">
                  <el-icon class="timeline-icon"><Timer /></el-icon>
                  <div class="timeline-content">
                    <div class="timeline-title">Started</div>
                    <div class="timeline-time">{{ formatTime(task.startTime) }}</div>
                  </div>
                </div>
                
                <template v-if="task.lastUpdateTime && task.status === 'completed'">
                  <div class="timeline-divider"></div>
                  <div class="timeline-item">
                    <el-icon class="timeline-icon"><SuccessFilled /></el-icon>
                    <div class="timeline-content">
                      <div class="timeline-title">Completed</div>
                      <div class="timeline-time">{{ formatTime(task.lastUpdateTime) }}</div>
                    </div>
                  </div>
                </template>
              </div>
            </div>
          </el-card>
        </transition-group>
      </div>
    </transition>
  </div>
</template>

<script>
import { computed } from 'vue';
import { useStore } from 'vuex';
import { 
  Download, 
  Box, 
  Timer, 
  SuccessFilled,
  DocumentCopy
} from '@element-plus/icons-vue';

export default {
  name: 'TaskHistory',
  
  components: {
    Timer,
    SuccessFilled,
    DocumentCopy
  },
  
  setup() {
    const store = useStore();
    
    // 获取任务历史
    const taskHistory = computed(() => store.state.task.taskHistory);
    
    // 获取任务图标
    const getTaskIcon = (task) => {
      if (task.type === 'download') {
        return Download;
      } else if (task.type === 'archive') {
        return Box;
      }
      return DocumentCopy;
    };
    
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
      getTaskIcon,
      formatBytes,
      formatTime,
    };
  },
};
</script>

<style scoped>
.task-history-view {
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

.empty-icon {
  font-size: 80px;
  color: var(--primary-color);
  opacity: 0.3;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.task-card {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.task-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
}

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

.task-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.task-property {
  margin-bottom: 8px;
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

.task-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 32px;
  margin: 16px 0;
  justify-content: start;
}

.stat-item {
  text-align: center;
  min-width: 100px;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--el-color-primary);
}

.stat-label {
  font-size: 0.85rem;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

.task-timeline {
  display: flex;
  align-items: center;
  margin-top: 8px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.timeline-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.timeline-icon {
  font-size: 20px;
  color: var(--el-color-primary);
}

.timeline-content {
  display: flex;
  flex-direction: column;
}

.timeline-title {
  font-weight: 500;
  font-size: 0.9rem;
}

.timeline-time {
  font-size: 0.85rem;
  color: var(--el-text-color-secondary);
}

.timeline-divider {
  height: 1px;
  background-color: var(--border-color);
  flex-grow: 1;
  margin: 0 12px;
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

.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* Responsive adjustments */
@media (max-width: 600px) {
  .task-stats {
    gap: 16px;
  }
  
  .stat-item {
    min-width: 80px;
  }
  
  .timeline-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .timeline-divider {
    display: none;
  }
  
  .task-timeline {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
}
</style> 