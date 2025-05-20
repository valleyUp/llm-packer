import api from '@/services/api';

// 任务管理模块
export default {
  namespaced: true,
  
  state: () => ({
    currentTask: null,
    taskHistory: [],
    isPolling: false,
    pollingInterval: null,
  }),
  
  mutations: {
    SET_CURRENT_TASK(state, task) {
      state.currentTask = task;
    },
    UPDATE_CURRENT_TASK(state, taskUpdate) {
      if (state.currentTask && state.currentTask.taskId === taskUpdate.taskId) {
        state.currentTask = { ...state.currentTask, ...taskUpdate };
      }
    },
    ADD_TO_HISTORY(state, task) {
      // 添加到历史记录，限制数量为10个
      const existingIndex = state.taskHistory.findIndex(t => t.taskId === task.taskId);
      if (existingIndex >= 0) {
        // 如果已存在，则更新
        state.taskHistory.splice(existingIndex, 1, task);
      } else {
        // 否则添加到顶部
        state.taskHistory.unshift(task);
        
        // 保持历史记录不超过10个
        if (state.taskHistory.length > 10) {
          state.taskHistory.pop();
        }
      }
    },
    SET_POLLING(state, status) {
      state.isPolling = status;
    },
    SET_POLLING_INTERVAL(state, interval) {
      state.pollingInterval = interval;
    },
    CLEAR_CURRENT_TASK(state) {
      state.currentTask = null;
    },
  },
  
  actions: {
    // 开始下载任务
    async startDownload({ commit, dispatch }, downloadParams) {
      try {
        const response = await api.startDownload(downloadParams);
        const task = response.data;
        
        commit('SET_CURRENT_TASK', task);
        commit('ADD_TO_HISTORY', task);
        
        // 启动轮询
        dispatch('startPolling', task.taskId);
        
        return task;
      } catch (error) {
        console.error('Error starting download:', error);
        throw error;
      }
    },
    
    // 创建归档任务
    async archiveModel({ commit, dispatch }, archiveParams) {
      try {
        const response = await api.archiveModel(archiveParams);
        const task = response.data;
        
        commit('SET_CURRENT_TASK', task);
        commit('ADD_TO_HISTORY', task);
        
        // 启动轮询
        dispatch('startPolling', task.taskId);
        
        return task;
      } catch (error) {
        console.error('Error starting archive task:', error);
        throw error;
      }
    },
    
    // 开始轮询任务状态
    startPolling({ commit, dispatch }, taskId) {
      commit('SET_POLLING', true);
      
      // 清除可能存在的旧定时器
      if (this.state.task.pollingInterval) {
        clearInterval(this.state.task.pollingInterval);
      }
      
      // 创建新的轮询定时器
      const interval = setInterval(() => {
        dispatch('pollTaskStatus', taskId);
      }, 1000); // 每秒更新一次
      
      commit('SET_POLLING_INTERVAL', interval);
    },
    
    // 轮询任务状态
    async pollTaskStatus({ commit, dispatch }, taskId) {
      try {
        const response = await api.getTaskStatus(taskId);
        const taskStatus = response.data;
        
        commit('UPDATE_CURRENT_TASK', taskStatus);
        commit('ADD_TO_HISTORY', taskStatus);
        
        // 如果任务完成、失败或被取消，停止轮询
        if (['completed', 'failed', 'cancelled'].includes(taskStatus.status)) {
          dispatch('stopPolling');
        }
        
        return taskStatus;
      } catch (error) {
        console.error('Error polling task status:', error);
        dispatch('stopPolling');
      }
    },
    
    // 停止轮询
    stopPolling({ commit, state }) {
      if (state.pollingInterval) {
        clearInterval(state.pollingInterval);
        commit('SET_POLLING_INTERVAL', null);
      }
      commit('SET_POLLING', false);
    },
    
    // 取消任务
    async cancelTask({dispatch }, taskId) {
      try {
        await api.cancelTask(taskId);
        
        // 停止轮询并更新状态
        dispatch('stopPolling');
        
        // 获取一次最终状态
        dispatch('pollTaskStatus', taskId);
        
        return true;
      } catch (error) {
        console.error('Error cancelling task:', error);
        throw error;
      }
    },
    
    // 清除当前任务
    clearCurrentTask({ commit, dispatch }) {
      dispatch('stopPolling');
      commit('CLEAR_CURRENT_TASK');
    },
  },
  
  getters: {
    // 获取与指定任务ID匹配的历史记录
    getTaskFromHistory: (state) => (taskId) => {
      return state.taskHistory.find(task => task.taskId === taskId);
    },
    
    // 获取已完成的任务
    completedTasks(state) {
      return state.taskHistory.filter(task => task.status === 'completed');
    },
    
    // 获取速率格式化
    formattedSpeed(state) {
      if (!state.currentTask || !state.currentTask.speed) {
        return '0 B/s';
      }
      
      const { speed } = state.currentTask;
      if (speed < 1024) {
        return `${speed.toFixed(1)} B/s`;
      } else if (speed < 1024 * 1024) {
        return `${(speed / 1024).toFixed(1)} KB/s`;
      } else {
        return `${(speed / (1024 * 1024)).toFixed(1)} MB/s`;
      }
    },
  },
}; 