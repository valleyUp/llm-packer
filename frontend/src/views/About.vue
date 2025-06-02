<template>
  <div class="about-view">
    <transition name="fade" appear>
      <h2 class="view-title">About LLM Weights Downloader</h2>
    </transition>
    
    <transition name="slide-fade" appear>
      <el-card class="about-card" :body-style="{ padding: '32px' }">
        <div class="about-content">
          <section class="about-section">
            <h3>
              <el-icon><InfoFilled /></el-icon>
              Overview
            </h3>
            <p class="about-text">
              LLM Weights Downloader is an advanced tool for downloading large language model weights from various sources,
              including Hugging Face and ModelScope. It provides features for downloading, filtering, and archiving model weights.
            </p>
          </section>
          
          <section class="about-section">
            <h3>
              <el-icon><StarFilled /></el-icon>
              Features
            </h3>
            <ul class="features-list">
              <li class="feature-item">
                <el-icon><Download /></el-icon>
                <span>Download models from Hugging Face and ModelScope</span>
              </li>
              <li class="feature-item">
                <el-icon><Scale /></el-icon>
                <span>Check model size before downloading</span>
              </li>
              <li class="feature-item">
                <el-icon><Filter /></el-icon>
                <span>Filter specific files using regex patterns</span>
              </li>
              <li class="feature-item">
                <el-icon><Box /></el-icon>
                <span>Archive downloaded models in various formats</span>
              </li>
              <li class="feature-item">
                <el-icon><Loading /></el-icon>
                <span>Track download progress and speed</span>
              </li>
              <li class="feature-item">
                <el-icon><List /></el-icon>
                <span>View download history</span>
              </li>
            </ul>
          </section>
          
          <section class="about-section">
            <h3>
              <el-icon><Connection /></el-icon>
              Supported Sources
            </h3>
            <div class="sources-list">
              <div class="source-card">
                <div class="source-icon huggingface-icon">
                  <svg viewBox="0 0 95 95" xmlns="http://www.w3.org/2000/svg">
                    <path d="M47.5 95C73.71 95 95 73.71 95 47.5S73.71 0 47.5 0 0 21.29 0 47.5 21.29 95 47.5 95z" fill="currentColor" opacity=".1"/>
                    <path d="M29.58 67.45c2.73 0 5.48-.56 7.74-1.71l.28-.14V44.4l-.49-.27a13.38 13.38 0 0 0-6.32-1.59c-7.62 0-12.18 5.82-12.18 12.73 0 7.73 5.31 12.18 10.97 12.18z M54.5 24.06c-6.79 0-12.25 5.24-12.25 11.76 0 6.45 5.46 11.69 12.25 11.69s12.16-5.24 12.16-11.69c0-6.52-5.37-11.76-12.16-11.76z M72.09 42.54a13.43 13.43 0 0 0-6.4 1.59l-.42.21v21.2l.28.14a14.22 14.22 0 0 0 7.74 1.77c5.79 0 10.96-4.45 10.96-12.18 0-6.97-4.23-12.73-12.16-12.73z" fill="currentColor"/>
                  </svg>
                </div>
                <div class="source-content">
                  <h4>Hugging Face</h4>
                  <p>Download models from the Hugging Face Hub, with support for authentication tokens and mirrors.</p>
                </div>
              </div>
              
              <div class="source-card">
                <div class="source-icon modelscope-icon">
                  <svg viewBox="0 0 95 95" xmlns="http://www.w3.org/2000/svg">
                    <path d="M47.5 95C73.71 95 95 73.71 95 47.5S73.71 0 47.5 0 0 21.29 0 47.5 21.29 95 47.5 95z" fill="currentColor" opacity=".1"/>
                    <path d="M28.58 31.45 47.5 20.27l18.92 11.18v22.37L47.5 65l-18.92-11.18V31.45z M25 28.5v25l22 13 22-13v-25l-22-13-22 13z" fill="currentColor"/>
                  </svg>
                </div>
                <div class="source-content">
                  <h4>ModelScope</h4>
                  <p>Download models from the ModelScope platform, with support for authentication tokens.</p>
                </div>
              </div>
            </div>
          </section>
          
          <section class="about-section">
            <h3>
              <el-icon><Box /></el-icon>
              Archive Formats
            </h3>
            <div class="formats-grid">
              <div class="format-item">
                <div class="format-icon">
                  <el-icon><Compass /></el-icon>
                </div>
                <div class="format-info">
                  <strong>ZIP</strong>
                  <span>Most compatible format, moderate compression</span>
                </div>
              </div>
              
              <div class="format-item">
                <div class="format-icon">
                  <el-icon><Collection /></el-icon>
                </div>
                <div class="format-info">
                  <strong>TAR</strong>
                  <span>Unix tape archive format, no compression</span>
                </div>
              </div>
              
              <div class="format-item">
                <div class="format-icon">
                  <el-icon><Connection /></el-icon>
                </div>
                <div class="format-info">
                  <strong>TAR.GZ</strong>
                  <span>TAR with gzip compression, good balance</span>
                </div>
              </div>
              
              <div class="format-item">
                <div class="format-icon">
                  <el-icon><Histogram /></el-icon>
                </div>
                <div class="format-info">
                  <strong>TAR.BZ2</strong>
                  <span>Better compression than gzip but slower</span>
                </div>
              </div>
              
              <div class="format-item">
                <div class="format-icon">
                  <el-icon><Star /></el-icon>
                </div>
                <div class="format-info">
                  <strong>TAR.XZ</strong>
                  <span>Best compression but slowest</span>
                </div>
              </div>
            </div>
          </section>
          
          <section class="about-section">
            <h3>
              <el-icon><Monitor /></el-icon>
              System Requirements
            </h3>
            <p class="about-text">
              The application requires sufficient disk space for downloading and processing large model files.
              Internet connection is required for downloading models from online sources.
            </p>
          </section>
          
          <div class="version-info">
            <div class="version-badge">Version 0.1.0</div>
          </div>
        </div>
      </el-card>
    </transition>
  </div>
</template>

<script>
import { 
  InfoFilled, 
  StarFilled, 
  Connection, 
  Box, 
  Download, 
  Scale, 
  Filter, 
  Loading, 
  List,
  Monitor,
  Compass,
  Collection,
  Histogram,
  Star
} from '@element-plus/icons-vue';

export default {
  name: 'AboutPage',
  
  components: {
    InfoFilled, 
    StarFilled, 
    Connection, 
    Box, 
    Download, 
    Scale, 
    Filter, 
    Loading, 
    List,
    Monitor,
    Compass,
    Collection,
    Histogram,
    Star
  }
};
</script>

<style scoped>
.about-view {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 16px;
}

.view-title {
  margin-bottom: 1.5rem;
  color: var(--primary-color);
  text-align: center;
  font-size: 2rem;
  font-weight: 600;
  letter-spacing: -0.01em;
}

.about-card {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  margin-bottom: 2rem;
  transition: all 0.3s ease;
}

.about-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
}

.about-content {
  line-height: 1.6;
}

.about-section {
  margin-bottom: 2rem;
}

.about-section h3 {
  color: var(--primary-color);
  font-size: 1.5rem;
  font-weight: 500;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 10px;
}

.about-section h3 .el-icon {
  font-size: 1.3rem;
}

.about-text {
  font-size: 1.02rem;
  color: var(--text-color);
  max-width: 800px;
}

.features-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  padding: 0;
  list-style-type: none;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  border-radius: 8px;
  background-color: rgba(var(--el-color-primary-rgb), 0.05);
  transition: transform 0.2s ease, background-color 0.2s ease;
}

.feature-item:hover {
  transform: translateY(-2px);
  background-color: rgba(var(--el-color-primary-rgb), 0.1);
}

.feature-item .el-icon {
  color: var(--primary-color);
  font-size: 1.2rem;
}

.sources-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
}

.source-card {
  display: flex;
  padding: 24px;
  border-radius: 12px;
  background-color: rgba(var(--el-color-primary-rgb), 0.05);
  transition: transform 0.2s ease, background-color 0.2s ease;
}

.source-card:hover {
  transform: translateY(-2px);
  background-color: rgba(var(--el-color-primary-rgb), 0.1);
}

.source-icon {
  width: 60px;
  height: 60px;
  margin-right: 16px;
  color: var(--primary-color);
}

.source-content {
  flex: 1;
}

.source-content h4 {
  margin: 0 0 8px 0;
  color: var(--primary-color);
  font-size: 1.2rem;
}

.source-content p {
  margin: 0;
  font-size: 0.95rem;
}

.formats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
}

.format-item {
  display: flex;
  align-items: center;
  padding: 16px;
  border-radius: 10px;
  background-color: rgba(var(--el-color-primary-rgb), 0.05);
  transition: transform 0.2s ease, background-color 0.2s ease;
}

.format-item:hover {
  transform: translateY(-2px);
  background-color: rgba(var(--el-color-primary-rgb), 0.1);
}

.format-icon {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 40px;
  height: 40px;
  margin-right: 16px;
  border-radius: 50%;
  background-color: rgba(var(--el-color-primary-rgb), 0.15);
  color: var(--primary-color);
}

.format-info {
  display: flex;
  flex-direction: column;
}

.format-info strong {
  margin-bottom: 4px;
  font-size: 1rem;
}

.format-info span {
  font-size: 0.85rem;
  color: var(--el-text-color-secondary);
}

.version-info {
  margin-top: 2.5rem;
  display: flex;
  justify-content: center;
}

.version-badge {
  display: inline-block;
  padding: 6px 16px;
  border-radius: 20px;
  background-color: var(--primary-color);
  color: white;
  font-size: 0.85rem;
  font-weight: 500;
}

/* Animation classes */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.3s ease-in;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .features-list,
  .sources-list,
  .formats-grid {
    grid-template-columns: 1fr;
  }
  
  .source-card {
    flex-direction: column;
  }
  
  .source-icon {
    width: 50px;
    height: 50px;
    margin: 0 0 16px 0;
  }
}
</style> 