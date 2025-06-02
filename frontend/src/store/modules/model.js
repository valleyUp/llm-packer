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
        
        // 记录原始响应
        console.log(`收到${source}原始响应:`, response);
        console.log(`响应数据类型:`, typeof response.data);
        console.log(`响应数据:`, JSON.stringify(response.data, null, 2));
        
        // 更严格的响应数据验证
        if (!response || !response.data) {
          throw new Error('Invalid response from server: No data received');
        }
        
        // 不同源的处理方式可能不同
        let modelSizeInfo;
        if (source === 'modelscope') {
          // 处理ModelScope响应 - 内联实现
          console.log('处理ModelScope响应:', response.data);
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
            console.error('处理ModelScope大小信息时出错:', e);
          }
          
          modelSizeInfo = {
            sizeGB: isNaN(sizeGB) ? 0 : sizeGB,
            message: data.message || ''
          };
        } else {
          // 直接处理响应数据，不进行类型验证
          const responseData = response.data;
          console.log(`${source}响应数据字段:`, Object.keys(responseData));
          
          // 直接提取数值并转换 - 强制处理
          let sizeGB;
          try {
            sizeGB = parseFloat(responseData.sizeGB);
            if (isNaN(sizeGB)) sizeGB = 0;
          } catch (e) {
            console.error('解析sizeGB时出错:', e);
            sizeGB = 0;
          }
          
          // 强制确保我们有有效数据
          modelSizeInfo = {
            sizeGB: sizeGB,
            message: String(responseData.message || '')
          };
        }
        
        console.log(`${source}标准化后的模型大小信息:`, modelSizeInfo);
        console.log(`${source}模型应该显示大小?: ${modelSizeInfo.sizeGB > 0}, sizeGB=${modelSizeInfo.sizeGB}`);
        
        // 设置模型大小信息
        commit('SET_MODEL_SIZE_INFO', modelSizeInfo);
        
        return response.data;
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