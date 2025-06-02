<template>
  <div class="app-container" :class="{ 'dark-mode': isDarkMode }">
    <header class="app-header">
      <h1 class="app-title">
        <el-icon class="app-logo-icon"><Connection /></el-icon>
        LLM Weights Downloader
      </h1>
      <div class="app-controls">
        <el-tooltip content="Toggle dark mode" placement="bottom">
          <el-switch
            v-model="darkMode"
            inline-prompt
            @change="toggleDarkMode"
          >
            <template #active-icon><el-icon><Moon /></el-icon></template>
            <template #inactive-icon><el-icon><Sunny /></el-icon></template>
          </el-switch>
        </el-tooltip>
      </div>
    </header>
    
    <nav class="app-nav">
      <div class="nav-container">
        <div class="nav-tabs" :class="{ 'mobile-nav': isMobileNav }">
          <router-link 
            to="/" 
            class="nav-tab" 
            :class="{ active: activeRoute === '/' }"
          >
            <el-icon><Download /></el-icon>
            <span>Download</span>
          </router-link>
          
          <router-link 
            to="/archive" 
            class="nav-tab" 
            :class="{ active: activeRoute === '/archive' }"
          >
            <el-icon><Box /></el-icon>
            <span>Archive</span>
          </router-link>
          
          <router-link 
            to="/history" 
            class="nav-tab" 
            :class="{ active: activeRoute === '/history' }"
          >
            <el-icon><List /></el-icon>
            <span>History</span>
          </router-link>
          
          <router-link 
            to="/about" 
            class="nav-tab" 
            :class="{ active: activeRoute === '/about' }"
          >
            <el-icon><InfoFilled /></el-icon>
            <span>About</span>
          </router-link>
          
          <div class="nav-indicator" :style="indicatorStyle"></div>
        </div>
      </div>
    </nav>
    
    <main class="app-content">
      <transition name="fade" mode="out-in">
        <router-view />
      </transition>
    </main>
    
    <footer class="app-footer">
      <div class="footer-content">
        <p>&copy; {{ currentYear }} LLM Weights Downloader</p>
        <div class="footer-links">
          <a href="https://github.com" target="_blank" class="footer-link">
            <el-icon><Link /></el-icon>
            GitHub
          </a>
          <a href="#" target="_blank" class="footer-link">
            <el-icon><Document /></el-icon>
            Documentation
          </a>
        </div>
      </div>
    </footer>
    
    <StagewiseToolbar v-if="isDev" :config="stagewiseConfig" />
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useStore } from 'vuex';
import { useRoute } from 'vue-router';
import { 
  Download, 
  Box, 
  List, 
  InfoFilled,
  Moon,
  Sunny,
  Link,
  Document,
  Connection
} from '@element-plus/icons-vue';

let StagewiseToolbar = null;
if (process.env.NODE_ENV === 'development') {
  ({ StagewiseToolbar } = await import('@stagewise/toolbar-vue'));
}

export default {
  name: 'App',
  
  components: {
    Download,
    Box,
    List,
    InfoFilled,
    Moon,
    Sunny,
    Link,
    Document,
    Connection,
    ...(StagewiseToolbar && { StagewiseToolbar }),
  },
  
  setup() {
    const store = useStore();
    const route = useRoute();
    
    // Compute active route
    const activeRoute = computed(() => route.path);
    
    // Menu position indicator style
    const indicatorStyle = computed(() => {
      const routes = ['/', '/archive', '/history', '/about'];
      const index = routes.indexOf(activeRoute.value);
      if (index === -1) return {};
      
      const width = 25; // Each tab takes 25% in desktop view
      return {
        left: `${width * index}%`,
        width: `${width}%`
      };
    });
    
    // Dark mode state
    const darkMode = ref(store.state.ui.darkMode);
    const isDarkMode = computed(() => store.state.ui.darkMode);
    
    // Mobile nav state
    const isMobileNav = ref(false);
    
    // Current year
    const currentYear = new Date().getFullYear();
    
    // Stagewise config
    const stagewiseConfig = {
      plugins: []
    };
    const isDev = process.env.NODE_ENV === 'development';
    
    // Toggle dark mode
    const toggleDarkMode = () => {
      store.dispatch('ui/toggleDarkMode');
    };
    
    // Check mobile status
    const checkMobileStatus = () => {
      store.dispatch('ui/checkMobileStatus');
      isMobileNav.value = window.innerWidth < 768;
    };
    
    // Mounted hook
    onMounted(() => {
      checkMobileStatus();
      window.addEventListener('resize', checkMobileStatus);
      
      // Apply slide-in animation for the app header
      setTimeout(() => {
        const header = document.querySelector('.app-header');
        if (header) header.classList.add('slide-in');
        
        const nav = document.querySelector('.app-nav');
        if (nav) nav.classList.add('slide-in');
      }, 100);
    });
    
    // Unmounted hook
    onUnmounted(() => {
      window.removeEventListener('resize', checkMobileStatus);
    });
    
    // Watch for route changes to animate content
    watch(route, () => {
      const content = document.querySelector('.app-content');
      if (content) {
        content.classList.add('content-transition');
        setTimeout(() => {
          content.classList.remove('content-transition');
        }, 300);
      }
    });
    
    return {
      activeRoute,
      darkMode,
      isDarkMode,
      currentYear,
      toggleDarkMode,
      stagewiseConfig,
      isDev,
      isMobileNav,
      indicatorStyle
    };
  },
};
</script>

<style>
:root {
  --primary-color: #409eff;
  --secondary-color: #67c23a;
  --accent-color: #f56c6c;
  --text-color: #333333;
  --text-secondary: #606266;
  --bg-color: #f5f7fa;
  --card-bg: #ffffff;
  --border-color: #e4e7ed;
  --header-bg: #ffffff;
  --nav-bg: #ffffff;
  --footer-bg: #ffffff;
  --hover-color: rgba(64, 158, 255, 0.1);
  --transition-speed: 0.3s;
  --shadow-sm: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 16px 0 rgba(0, 0, 0, 0.08);
  --shadow-lg: 0 8px 24px 0 rgba(0, 0, 0, 0.12);
  --border-radius: 12px;
  --border-radius-lg: 16px;
}

.dark-mode {
  --primary-color: #4dabff;
  --secondary-color: #85ce61;
  --accent-color: #ff7875;
  --text-color: #e5e7eb;
  --text-secondary: #a0a0a0;
  --bg-color: #121212;
  --card-bg: #1e1e1e;
  --border-color: #303030;
  --header-bg: #1e1e1e;
  --nav-bg: #1e1e1e;
  --footer-bg: #1e1e1e;
  --hover-color: rgba(77, 171, 255, 0.2);
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
  background-color: var(--bg-color);
  color: var(--text-color);
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  transition: all var(--transition-speed) ease;
}

/* Header styles */
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: var(--header-bg);
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: var(--shadow-sm);
  transform: translateY(-100%);
  opacity: 0;
  transition: transform 0.5s ease, opacity 0.5s ease;
}

.app-header.slide-in {
  transform: translateY(0);
  opacity: 1;
}

.app-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--primary-color);
  display: flex;
  align-items: center;
  gap: 8px;
}

.app-logo-icon {
  font-size: 1.8rem;
}

.app-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* Nav styles */
.app-nav {
  background-color: var(--nav-bg);
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 64px;
  z-index: 99;
  box-shadow: var(--shadow-sm);
  transform: translateY(-100%);
  opacity: 0;
  transition: transform 0.5s ease 0.1s, opacity 0.5s ease 0.1s;
}

.app-nav.slide-in {
  transform: translateY(0);
  opacity: 1;
}

.nav-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 16px;
}

.nav-tabs {
  display: flex;
  position: relative;
  height: 54px;
}

.nav-tab {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 10px 0;
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
  position: relative;
  transition: color var(--transition-speed) ease;
  overflow: hidden;
}

.nav-tab:hover {
  color: var(--primary-color);
}

.nav-tab.active {
  color: var(--primary-color);
}

.nav-tab .el-icon {
  font-size: 1.2rem;
  margin-bottom: 4px;
  transition: transform 0.2s ease;
}

.nav-tab:hover .el-icon {
  transform: translateY(-2px);
}

.nav-indicator {
  position: absolute;
  bottom: 0;
  height: 3px;
  background-color: var(--primary-color);
  border-radius: 3px 3px 0 0;
  transition: all 0.3s ease;
}

/* Content styles */
.app-content {
  flex: 1;
  padding: 2rem 0;
  width: 100%;
  transition: opacity 0.3s ease;
}

.app-content.content-transition {
  opacity: 0.6;
}

/* Footer styles */
.app-footer {
  padding: 1.5rem;
  background-color: var(--footer-bg);
  border-top: 1px solid var(--border-color);
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.footer-content {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.footer-links {
  display: flex;
  gap: 16px;
}

.footer-link {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--primary-color);
  text-decoration: none;
  font-size: 0.85rem;
  transition: opacity 0.2s ease;
}

.footer-link:hover {
  opacity: 0.8;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Mobile styles */
@media (max-width: 768px) {
  .app-header {
    padding: 1rem;
  }
  
  .app-title {
    font-size: 1.2rem;
  }
  
  .nav-tab span {
    font-size: 0.8rem;
  }
  
  .footer-content {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
}

/* Element Plus overrides */
.el-menu--horizontal {
  border-bottom: none !important;
}

.el-card {
  border: none !important;
  transition: all var(--transition-speed) ease;
}

.el-button {
  border-radius: 8px;
}

.el-button--primary {
  background-color: var(--primary-color);
}

.el-input__wrapper,
.el-select__wrapper {
  border-radius: 8px !important;
}

/* Fix for any unwanted transitions when changing themes */
.el-input__wrapper,
.el-select__wrapper,
.el-button,
.el-card,
.el-tag,
.el-progress-bar__outer {
  transition: background-color var(--transition-speed) ease, 
              border-color var(--transition-speed) ease, 
              color var(--transition-speed) ease, 
              box-shadow var(--transition-speed) ease;
}
</style> 