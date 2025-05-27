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
        console.log(`开始检查${source}模型大小:`, { source, modelId });
        const response = await api.checkModelSize({
          source,
          modelId,
          authToken,
        });
        
        console.log(`收到${source}模型大小响应:`, response);
        
        // 更严格的响应数据验证
        if (!response || !response.data) {
          throw new Error('Invalid response from server: No data received');
        }
        
        // 验证数据包含必要字段，处理不同源的响应格式
        const responseData = response.data;
        console.log(`${source}响应数据字段:`, Object.keys(responseData));
        
        // 确保sizeGB是数值类型
        let sizeGB = responseData.sizeGB;
        if (typeof sizeGB === 'string') {
          sizeGB = parseFloat(sizeGB);
        }
        
        // 标准化响应数据格式
        const modelSizeInfo = {
          sizeGB: typeof sizeGB === 'number' && !isNaN(sizeGB) ? sizeGB : 0,
          message: responseData.message || ''
        };
        
        console.log(`${source}标准化后的模型大小信息:`, modelSizeInfo);
        
        // 明确记录是否该显示模型大小
        const shouldShowSize = modelSizeInfo.sizeGB > 0;
        console.log(`${source}模型应该显示大小?: ${shouldShowSize}, sizeGB=${modelSizeInfo.sizeGB}`);
        
        // 设置模型大小信息
        commit('SET_MODEL_SIZE_INFO', modelSizeInfo);
        
        return responseData;
      } catch (error) {
        console.error(`检查${source}模型大小时出错:`, error);
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
      // 提供详细日志
      console.log('modelSizeFormatted执行:', state.modelSizeInfo);
      
      if (!state.modelSizeInfo) {
        console.log('无模型大小信息');
        return null;
      }
      
      // 处理各种可能的数据类型
      let sizeGB;
      
      if (state.modelSizeInfo.sizeGB === undefined || state.modelSizeInfo.sizeGB === null) {
        console.log('sizeGB字段不存在');
        return null;
      }
      
      if (typeof state.modelSizeInfo.sizeGB === 'string') {
        sizeGB = parseFloat(state.modelSizeInfo.sizeGB);
        console.log('sizeGB是字符串，解析为:', sizeGB);
      } else {
        sizeGB = state.modelSizeInfo.sizeGB;
        console.log('sizeGB是数值:', sizeGB);
      }
      
      // 更严格的条件检查
      if (isNaN(sizeGB) || sizeGB <= 0) {
        console.log('sizeGB无效或为0');
        return null;
      }
      
      // 格式化为2位小数
      console.log('返回格式化的大小:', `${sizeGB.toFixed(2)} GB`);
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