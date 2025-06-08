import React, { useContext, useState } from 'react';
import {
  Download,
  Globe,
  Key,
  FolderOpen,
  Filter,
  Archive,
  CheckCircle,
  AlertCircle,
  Loader,
  Zap,
  Shield,
  Cpu
} from 'lucide-react';
import { TaskContext } from '../TaskContext';
import { api } from '../api';

export default function DownloadPage() {
  const { currentTask, startDownload, cancelTask } = useContext(TaskContext);
  const [form, setForm] = useState({
    source: 'huggingface',
    modelId: '',
    authToken: '',
    hfMirror: '',
    savePath: '',
    fileFilter: '',
    archiveAfter: false,
    targetDrivePath: '',
    archiveName: '',
    archiveFormat: 'zip'
  });
  const [checking, setChecking] = useState(false);
  const [sizeInfo, setSizeInfo] = useState(null);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm({ ...form, [name]: type === 'checkbox' ? checked : value });
  };

  const handleCheckSize = async () => {
    if (!form.modelId) return;
    setChecking(true);
    setError('');
    try {
      const data = await api.checkModelSize({ source: form.source, modelId: form.modelId, authToken: form.authToken });
      setSizeInfo(data);
    } catch (e) {
      setError('Failed to check size');
    } finally {
      setChecking(false);
    }
  };

  const handleStart = async () => {
    try {
      await startDownload(form);
    } catch {
      setError('Failed to start download');
    }
  };

  return (
    <div className="page">
      <section className="hero">
        <div className="hero-content">
          <div className="hero-text">
            <div className="hero-icon-wrapper">
              <Download className="hero-icon" />
            </div>
            <h1>LLM Weights Downloader</h1>
            <p>Fast, reliable, and secure model downloads with intelligent archiving capabilities.</p>
            <div className="hero-features">
              <div className="feature-item">
                <Zap />
                <span>Lightning Fast</span>
              </div>
              <div className="feature-item">
                <Shield />
                <span>Secure Downloads</span>
              </div>
              <div className="feature-item">
                <Cpu />
                <span>AI Optimized</span>
              </div>
            </div>
          </div>
          <div className="hero-visual">
            <img
              className="hero-img"
              src="https://images.unsplash.com/photo-1677442136019-21780ecad995?w=600&h=400&fit=crop&crop=center"
              alt="AI and Machine Learning"
            />
            <div className="hero-gradient"></div>
          </div>
        </div>
      </section>
      <div className="download-section">
        <h2>Configure Download</h2>
        <div className="form-section">
          <div className="form-row">
            <div className="form-group">
              <label>
                Source Platform
                <select name="source" value={form.source} onChange={handleChange} className="select-with-emoji">
                  <option value="huggingface">🤗 Hugging Face</option>
                  <option value="modelscope">🔬 ModelScope</option>
                </select>
              </label>
            </div>
            <div className="form-group">
              <label>
                Model ID/URL
                <div className="input-group">
                  <Cpu />
                  <input
                    name="modelId"
                    value={form.modelId}
                    onChange={handleChange}
                    className="with-icon"
                    placeholder="e.g., microsoft/DialoGPT-medium"
                  />
                </div>
              </label>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>
                Authentication Token
                <div className="input-group">
                  <Key />
                  <input
                    name="authToken"
                    value={form.authToken}
                    onChange={handleChange}
                    type="password"
                    className="with-icon"
                    placeholder="Optional: Your access token"
                  />
                </div>
              </label>
            </div>
            {form.source === 'huggingface' && (
              <div className="form-group">
                <label>
                  HF Mirror (Optional)
                  <div className="input-group">
                    <Globe />
                    <input
                      name="hfMirror"
                      value={form.hfMirror}
                      onChange={handleChange}
                      className="with-icon"
                      placeholder="Custom mirror URL"
                    />
                  </div>
                </label>
              </div>
            )}
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>
                Save Path
                <div className="input-group">
                  <FolderOpen />
                  <input
                    name="savePath"
                    value={form.savePath}
                    onChange={handleChange}
                    className="with-icon"
                    placeholder="/path/to/save/models"
                  />
                </div>
              </label>
            </div>
            <div className="form-group">
              <label>
                File Filter (Optional)
                <div className="input-group">
                  <Filter />
                  <input
                    name="fileFilter"
                    value={form.fileFilter}
                    onChange={handleChange}
                    className="with-icon"
                    placeholder="*.bin,*.safetensors"
                  />
                </div>
              </label>
            </div>
          </div>

          <div className="form-actions">
            <button
              className="btn btn-secondary"
              onClick={handleCheckSize}
              disabled={checking || !form.modelId}
            >
              {checking ? <Loader className="animate-spin" /> : <CheckCircle />}
              {checking ? 'Checking...' : 'Check Size'}
            </button>

            {sizeInfo && (
              <div className="size-info-card">
                <CheckCircle className="text-success" />
                <div>
                  <strong>Size: {sizeInfo.sizeGB} GB</strong>
                  <p>{sizeInfo.message}</p>
                </div>
              </div>
            )}
          </div>

          <div className="archive-section">
            <div className="toggle-section">
              <div className="toggle-content">
                <div className="toggle-info">
                  <h4>Archive After Download</h4>
                  <p>Automatically compress and archive your downloaded models for efficient storage</p>
                </div>
                <label className="toggle-switch">
                  <input
                    type="checkbox"
                    name="archiveAfter"
                    checked={form.archiveAfter}
                    onChange={handleChange}
                  />
                  <span className="toggle-slider">
                    <span className="toggle-button">
                      {form.archiveAfter ? <CheckCircle /> : <Archive />}
                    </span>
                  </span>
                </label>
              </div>
            </div>

            {form.archiveAfter && (
              <div className="archive-options">
                <div className="form-row">
                  <div className="form-group">
                    <label>
                      Target Drive Path
                      <div className="input-group">
                        <FolderOpen />
                        <input
                          name="targetDrivePath"
                          value={form.targetDrivePath}
                          onChange={handleChange}
                          className="with-icon"
                          placeholder="/path/to/archive/drive"
                        />
                      </div>
                    </label>
                  </div>
                  <div className="form-group">
                    <label>
                      Archive Name
                      <div className="input-group">
                        <Archive />
                        <input
                          name="archiveName"
                          value={form.archiveName}
                          onChange={handleChange}
                          className="with-icon"
                          placeholder="my-model-archive"
                        />
                      </div>
                    </label>
                  </div>
                </div>
                <div className="form-group">
                  <label>
                    Archive Format
                    <select name="archiveFormat" value={form.archiveFormat} onChange={handleChange} className="select-with-emoji">
                      <option value="zip">📦 ZIP (Recommended)</option>
                      <option value="tar">📄 TAR</option>
                      <option value="gztar">🗜️ TAR.GZ (Compressed)</option>
                      <option value="bztar">🗜️ TAR.BZ2 (High Compression)</option>
                      <option value="xztar">🗜️ TAR.XZ (Best Compression)</option>
                    </select>
                  </label>
                </div>
              </div>
            )}
          </div>

          {error && (
            <div className="error-card">
              <AlertCircle />
              <span>{error}</span>
            </div>
          )}

          <div className="form-submit">
            <button
              className="btn btn-primary"
              onClick={handleStart}
              disabled={!form.modelId || !form.savePath}
            >
              <Download />
              Start Download
            </button>
          </div>
        </div>
      </div>

      {currentTask && (
        <div className="task-status-card">
          <div className="task-header">
            <div className="task-info">
              <h3>Download in Progress</h3>
              <p>Status: {currentTask.status}</p>
            </div>
            <button
              className="btn btn-error"
              onClick={() => cancelTask(currentTask.taskId)}
            >
              Cancel
            </button>
          </div>

          <div className="progress-section">
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${currentTask.progress || 0}%` }}
              ></div>
            </div>
            <div className="progress-text">
              {Math.round(currentTask.progress || 0)}% Complete
            </div>
          </div>

          <div className="task-details">
            <div className="detail-item">
              <Cpu />
              <span>Model: {currentTask.modelId || 'Processing...'}</span>
            </div>
            <div className="detail-item">
              <Download />
              <span>Type: {currentTask.type || 'download'}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
