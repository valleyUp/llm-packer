import api from '@/services/api';

// 模型数据模块
export default {
  namespaced: true,
  
  state: () => ({
    modelSizeInfo: null,
    isCheckingSize: false,
    lastError: null,
  }),
  
  mutations: {
    SET_MODEL_SIZE_INFO(state, info) {
      state.modelSizeInfo = info;
    },
    SET_CHECKING_SIZE(state, status) {
      state.isCheckingSize = status;
    },
    SET_ERROR(state, error) {
      state.lastError = error;
    },
    CLEAR_ERROR(state) {
      state.lastError = null;
    },
  },
  
  actions: {
    // 检查模型大小
    async checkModelSize({ commit }, { source, modelId, authToken }) {
      commit('SET_CHECKING_SIZE', true);
      commit('CLEAR_ERROR');
      
      try {
        console.log('Sending request to check model size:', { source, modelId });
        const response = await api.checkModelSize({
          source,
          modelId,
          authToken,
        });
        
        console.log('Received model size response:', response);
        
        // 更严格的响应数据验证
        if (!response || !response.data) {
          throw new Error('Invalid response from server: No data received');
        }
        
        // 验证数据包含必要字段
        const { sizeGB, message } = response.data;
        if (sizeGB === undefined || message === undefined) {
          console.error('Missing required fields in response:', response.data);
          throw new Error('Invalid response format: Missing required fields');
        }
        
        // 设置模型大小信息
        commit('SET_MODEL_SIZE_INFO', {
          sizeGB: typeof sizeGB === 'number' ? sizeGB : 0,
          message: typeof message === 'string' ? message : 'Unknown message'
        });
        
        return response.data;
      } catch (error) {
        console.error('Error checking model size:', error);
        // 设置错误状态，但同时也提供空的模型大小信息，以确保UI能正确显示
        commit('SET_MODEL_SIZE_INFO', {
          sizeGB: 0,
          message: `Error: ${error.response?.data?.detail || error.message || 'Unknown error'}`
        });
        commit('SET_ERROR', error.response?.data?.detail || error.message);
        throw error;
      } finally {
        commit('SET_CHECKING_SIZE', false);
      }
    },
    
    // 清除模型大小信息
    clearModelSizeInfo({ commit }) {
      commit('SET_MODEL_SIZE_INFO', null);
    },
  },
  
  getters: {
    modelSizeFormatted(state) {
      if (!state.modelSizeInfo) {
        return null;
      }
      
      // API returns 'sizeGB' as per backend schema
      const sizeGB = Number(state.modelSizeInfo.sizeGB);
      if (isNaN(sizeGB) || sizeGB === 0) {
        return null;
      }
      
      // Format with 2 decimal places
      return `${sizeGB.toFixed(2)} GB`;
    },
    
    modelSizeMessage(state) {
      if (!state.modelSizeInfo) {
        return '';
      }
      
      // API returns 'message' as per backend schema
      return state.modelSizeInfo.message || '';
    },
    
    compressedSizeEstimate(state) {
      if (!state.modelSizeInfo) {
        return null;
      }
      
      const sizeGB = Number(state.modelSizeInfo.sizeGB);
      if (isNaN(sizeGB) || sizeGB === 0) {
        return null;
      }
      
      // 假设压缩后大约为原始大小的70%
      const compressedSize = sizeGB * 0.7;
      return `${compressedSize.toFixed(2)} GB (estimated)`;
    },
  },
}; 