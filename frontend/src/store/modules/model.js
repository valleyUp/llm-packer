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
        
        // 更严格的响应数据验证
        if (!response || !response.data) {
          throw new Error('Invalid response from server: No data received');
        }
        
        // 不同源的处理方式可能不同
        let modelSizeInfo;
        if (source === 'modelscope') {
          // 处理ModelScope响应 - 内联实现
          const data = response.data;
          let sizeGB = 0;
          
          try {
            // 尝试多种方式提取大小值
            if (typeof data.sizeGB === 'number') {
              sizeGB = data.sizeGB;
            } else if (typeof data.sizeGB === 'string') {
              sizeGB = parseFloat(data.sizeGB);
            }
            
            // 如果还是无效，尝试从消息中提取
            if (isNaN(sizeGB) || sizeGB <= 0) {
              const message = data.message || '';
              const sizeMatch = message.match(/(\d+\.\d+)\s*GB/);
              if (sizeMatch && sizeMatch[1]) {
                sizeGB = parseFloat(sizeMatch[1]);
              }
            }
          } catch (e) {
            // 静默处理错误
          }
          
          modelSizeInfo = {
            sizeGB: isNaN(sizeGB) ? 0 : sizeGB,
            message: data.message || ''
          };
        } else {
          // 直接处理响应数据，不进行类型验证
          const responseData = response.data;
          
          // 直接提取数值并转换 - 强制处理
          let sizeGB;
          try {
            sizeGB = parseFloat(responseData.sizeGB);
            if (isNaN(sizeGB)) sizeGB = 0;
          } catch (e) {
            sizeGB = 0;
          }
          
          // 强制确保我们有有效数据
          modelSizeInfo = {
            sizeGB: sizeGB,
            message: String(responseData.message || '')
          };
        }
        
        // 设置模型大小信息
        commit('SET_MODEL_SIZE_INFO', modelSizeInfo);
        
        return response.data;
      } catch (error) {
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
      
      // 处理各种可能的数据类型
      let sizeGB;
      
      if (state.modelSizeInfo.sizeGB === undefined || state.modelSizeInfo.sizeGB === null) {
        return null;
      }
      
      if (typeof state.modelSizeInfo.sizeGB === 'string') {
        sizeGB = parseFloat(state.modelSizeInfo.sizeGB);
      } else {
        sizeGB = state.modelSizeInfo.sizeGB;
      }
      
      // 更严格的条件检查
      if (isNaN(sizeGB) || sizeGB <= 0) {
        return null;
      }
      
      // 格式化为2位小数
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
      
      // 直接使用sizeGB进行计算，不依赖其他getter
      let sizeGB;
      
      if (typeof state.modelSizeInfo.sizeGB === 'string') {
        sizeGB = parseFloat(state.modelSizeInfo.sizeGB);
      } else {
        sizeGB = state.modelSizeInfo.sizeGB;
      }
      
      if (isNaN(sizeGB) || sizeGB <= 0) {
        return null;
      }
      
      // 假设压缩后大约为原始大小的70%
      const compressedSize = sizeGB * 0.7;
      return `${compressedSize.toFixed(2)} GB (estimated)`;
    },
  },
}; 