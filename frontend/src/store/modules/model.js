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
        const response = await api.checkModelSize({
          source,
          modelId,
          authToken,
        });
        
        commit('SET_MODEL_SIZE_INFO', response.data);
        return response.data;
      } catch (error) {
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
      if (!state.modelSizeInfo || state.modelSizeInfo.sizeGB === 0) {
        return null;
      }
      return `${state.modelSizeInfo.sizeGB.toFixed(2)} GB`;
    },
    
    modelSizeMessage(state) {
      if (!state.modelSizeInfo) {
        return '';
      }
      return state.modelSizeInfo.message;
    },
    
    compressedSizeEstimate(state) {
      if (!state.modelSizeInfo || state.modelSizeInfo.sizeGB === 0) {
        return null;
      }
      
      // 假设压缩后大约为原始大小的70%
      const compressedSize = state.modelSizeInfo.sizeGB * 0.7;
      return `${compressedSize.toFixed(2)} GB (estimated)`;
    },
  },
}; 