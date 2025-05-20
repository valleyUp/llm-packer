import axios from 'axios';

// 创建axios实例
const apiClient = axios.create({
  baseURL: process.env.VUE_APP_API_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60秒超时
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 这里可以添加认证令牌等
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response || error);
    return Promise.reject(error);
  }
);

// API服务对象
const api = {
  // 检查模型大小
  checkModelSize(params) {
    return apiClient.post('/check-size', params);
  },
  
  // 开始下载任务
  startDownload(params) {
    return apiClient.post('/download/start', params);
  },
  
  // 获取任务状态
  getTaskStatus(taskId) {
    return apiClient.get(`/download/progress/${taskId}`);
  },
  
  // 取消任务
  cancelTask(taskId) {
    return apiClient.post(`/download/cancel/${taskId}`);
  },
  
  // 创建归档任务
  archiveModel(params) {
    return apiClient.post('/archive', params);
  },
  
  // 健康检查
  healthCheck() {
    return apiClient.get('/health');
  },
};

export default api; 