// UI状态管理模块
export default {
  namespaced: true,
  
  state: () => ({
    darkMode: false,
    notifications: [],
    activeTab: 'download',
    isMobile: false,
  }),
  
  mutations: {
    SET_DARK_MODE(state, isDark) {
      state.darkMode = isDark;
    },
    ADD_NOTIFICATION(state, notification) {
      state.notifications.push({
        id: Date.now(),
        ...notification,
      });
    },
    REMOVE_NOTIFICATION(state, notificationId) {
      state.notifications = state.notifications.filter(n => n.id !== notificationId);
    },
    SET_ACTIVE_TAB(state, tab) {
      state.activeTab = tab;
    },
    SET_IS_MOBILE(state, isMobile) {
      state.isMobile = isMobile;
    },
  },
  
  actions: {
    toggleDarkMode({ commit, state }) {
      commit('SET_DARK_MODE', !state.darkMode);
    },
    
    showNotification({ commit }, { message, type = 'info', duration = 3000 }) {
      const notification = {
        message,
        type,
        duration,
      };
      
      commit('ADD_NOTIFICATION', notification);
      
      // 自动移除通知
      if (duration > 0) {
        setTimeout(() => {
          commit('REMOVE_NOTIFICATION', notification.id);
        }, duration);
      }
      
      return notification.id;
    },
    
    dismissNotification({ commit }, notificationId) {
      commit('REMOVE_NOTIFICATION', notificationId);
    },
    
    setActiveTab({ commit }, tab) {
      commit('SET_ACTIVE_TAB', tab);
    },
    
    checkMobileStatus({ commit }) {
      const isMobile = window.innerWidth < 768;
      commit('SET_IS_MOBILE', isMobile);
    },
  },
  
  getters: {
    currentTheme(state) {
      return state.darkMode ? 'dark' : 'light';
    },
  },
}; 