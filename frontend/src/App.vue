<template>
  <div class="app-container" :class="{ 'dark-mode': isDarkMode }">
    <header class="app-header">
      <h1 class="app-title">LLM Weights Downloader</h1>
      <div class="app-controls">
        <el-switch
          v-model="darkMode"
          active-text="Dark"
          inactive-text="Light"
          @change="toggleDarkMode"
        />
      </div>
    </header>
    
    <nav class="app-nav">
      <el-menu
        :default-active="activeRoute"
        mode="horizontal"
        router
        :ellipsis="false"
        :background-color="menuBgColor"
        :text-color="menuTextColor"
        :active-text-color="menuActiveColor"
      >
        <el-menu-item index="/">
          <el-icon><Download /></el-icon>
          <span>Download</span>
        </el-menu-item>
        <el-menu-item index="/archive">
          <el-icon><Files /></el-icon>
          <span>Archive</span>
        </el-menu-item>
        <el-menu-item index="/history">
          <el-icon><List /></el-icon>
          <span>History</span>
        </el-menu-item>
        <el-menu-item index="/about">
          <el-icon><InfoFilled /></el-icon>
          <span>About</span>
        </el-menu-item>
      </el-menu>
    </nav>
    
    <main class="app-content">
      <router-view />
    </main>
    
    <footer class="app-footer">
      <p>&copy; {{ currentYear }} LLM Weights Downloader</p>
    </footer>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useStore } from 'vuex';
import { useRoute } from 'vue-router';
import { Download, Files, List, InfoFilled } from '@element-plus/icons-vue';

export default {
  name: 'App',
  
  components: {
    Download,
    Files,
    List,
    InfoFilled,
  },
  
  setup() {
    const store = useStore();
    const route = useRoute();
    
    // 计算当前路由
    const activeRoute = computed(() => route.path);
    
    // 深色模式状态
    const darkMode = ref(store.state.ui.darkMode);
    const isDarkMode = computed(() => store.state.ui.darkMode);
    
    // 菜单颜色
    const menuBgColor = computed(() => isDarkMode.value ? '#1f2937' : '#ffffff');
    const menuTextColor = computed(() => isDarkMode.value ? '#e5e7eb' : '#606266');
    const menuActiveColor = computed(() => '#409eff');
    
    // 当前年份
    const currentYear = new Date().getFullYear();
    
    // 切换深色模式
    const toggleDarkMode = () => {
      store.dispatch('ui/toggleDarkMode');
    };
    
    // 检查移动设备状态
    const checkMobileStatus = () => {
      store.dispatch('ui/checkMobileStatus');
    };
    
    // 组件挂载时
    onMounted(() => {
      checkMobileStatus();
      window.addEventListener('resize', checkMobileStatus);
    });
    
    // 组件卸载时
    onUnmounted(() => {
      window.removeEventListener('resize', checkMobileStatus);
    });
    
    return {
      activeRoute,
      darkMode,
      isDarkMode,
      menuBgColor,
      menuTextColor,
      menuActiveColor,
      currentYear,
      toggleDarkMode,
    };
  },
};
</script>

<style>
:root {
  --primary-color: #409eff;
  --text-color: #303133;
  --bg-color: #f5f7fa;
  --card-bg: #ffffff;
  --border-color: #e4e7ed;
}

.dark-mode {
  --primary-color: #409eff;
  --text-color: #e5e7eb;
  --bg-color: #111827;
  --card-bg: #1f2937;
  --border-color: #374151;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--bg-color);
  color: var(--text-color);
  transition: all 0.3s ease;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: var(--card-bg);
  border-bottom: 1px solid var(--border-color);
}

.app-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--primary-color);
}

.app-nav {
  background-color: var(--card-bg);
  border-bottom: 1px solid var(--border-color);
}

.app-content {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}

.app-footer {
  padding: 1rem;
  text-align: center;
  font-size: 0.9rem;
  background-color: var(--card-bg);
  border-top: 1px solid var(--border-color);
}

@media (max-width: 768px) {
  .app-header {
    padding: 1rem;
    flex-direction: column;
    gap: 1rem;
  }
  
  .app-content {
    padding: 1rem;
  }
}
</style> 