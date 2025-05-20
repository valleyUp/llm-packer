<template>
  <div class="about-view">
    <h2 class="view-title">About LLM Weights Downloader</h2>
    
    <el-card class="about-card">
      <div class="about-content">
        <h3>Overview</h3>
        <p>
          LLM Weights Downloader is an advanced tool for downloading large language model weights from various sources,
          including Hugging Face and ModelScope. It provides features for downloading, filtering, and archiving model weights.
        </p>
        
        <h3>Features</h3>
        <ul>
          <li>Download models from Hugging Face and ModelScope</li>
          <li>Check model size before downloading</li>
          <li>Filter specific files using regex patterns</li>
          <li>Archive downloaded models in various formats</li>
          <li>Track download progress and speed</li>
          <li>View download history</li>
        </ul>
        
        <h3>Supported Sources</h3>
        <div class="sources-list">
          <div class="source-item">
            <h4>Hugging Face</h4>
            <p>Download models from the Hugging Face Hub, with support for authentication tokens and mirrors.</p>
          </div>
          
          <div class="source-item">
            <h4>ModelScope</h4>
            <p>Download models from the ModelScope platform, with support for authentication tokens.</p>
          </div>
        </div>
        
        <h3>Archive Formats</h3>
        <ul>
          <li><strong>ZIP</strong> - Most compatible format, moderate compression</li>
          <li><strong>TAR</strong> - Unix tape archive format, no compression</li>
          <li><strong>TAR.GZ</strong> - TAR with gzip compression, good balance of speed and size</li>
          <li><strong>TAR.BZ2</strong> - TAR with bzip2 compression, better compression than gzip but slower</li>
          <li><strong>TAR.XZ</strong> - TAR with xz compression, best compression but slowest</li>
        </ul>
        
        <h3>System Requirements</h3>
        <p>
          The application requires sufficient disk space for downloading and processing large model files.
          Internet connection is required for downloading models from online sources.
        </p>
        
        <div class="version-info">
          <p>Version: 0.1.0</p>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
export default {
  name: 'AboutPage',
};
</script>

<style scoped>
.about-view {
  max-width: 800px;
  margin: 0 auto;
}

.view-title {
  margin-bottom: 1.5rem;
  color: var(--primary-color);
  text-align: center;
}

.about-card {
  margin-bottom: 2rem;
}

.about-content {
  line-height: 1.6;
}

.about-content h3 {
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  color: var(--primary-color);
}

.about-content h3:first-child {
  margin-top: 0;
}

.about-content p {
  margin-bottom: 1rem;
}

.about-content ul {
  margin-bottom: 1rem;
  padding-left: 1.5rem;
}

.about-content li {
  margin-bottom: 0.5rem;
}

.sources-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.source-item {
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
}

.source-item h4 {
  margin-bottom: 0.5rem;
  color: var(--primary-color);
}

.version-info {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
  font-size: 0.9rem;
  color: #909399;
}
</style> 