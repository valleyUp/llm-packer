import React, { useContext, useState } from 'react';
import { TaskContext } from '../TaskContext';
import { api } from '../api';
import downloadIcon from '../assets/download-icon.svg';

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
        <div className="hero-text">
          <img src={downloadIcon} alt="download" className="hero-icon" />
          <h1>LLM Weights Downloader</h1>
          <p>Fast, reliable model downloads and archiving.</p>
        </div>
        <img className="hero-img" src="https://source.unsplash.com/featured/?machine-learning" alt="AI abstract" />
      </section>
      <h2>Download Model</h2>
      <div className="form-section">
        <label>
          Source
          <select name="source" value={form.source} onChange={handleChange}>
            <option value="huggingface">Hugging Face</option>
            <option value="modelscope">ModelScope</option>
          </select>
        </label>
        <label>
          Model ID/URL
          <input name="modelId" value={form.modelId} onChange={handleChange} />
        </label>
        <label>
          Auth Token
          <input name="authToken" value={form.authToken} onChange={handleChange} type="password" />
        </label>
        {form.source === 'huggingface' && (
          <label>
            HF Mirror
            <input name="hfMirror" value={form.hfMirror} onChange={handleChange} />
          </label>
        )}
        <label>
          Save Path
          <input name="savePath" value={form.savePath} onChange={handleChange} />
        </label>
        <label>
          File Filter
          <input name="fileFilter" value={form.fileFilter} onChange={handleChange} />
        </label>
        <button className="btn-secondary" onClick={handleCheckSize} disabled={checking}>Check Size</button>
        {sizeInfo && (
          <div className="size-info">Size: {sizeInfo.sizeGB} GB {sizeInfo.message}</div>
        )}
        <label className="checkbox">
          <input type="checkbox" name="archiveAfter" checked={form.archiveAfter} onChange={handleChange} /> Archive after download
        </label>
        {form.archiveAfter && (
          <div className="archive-options">
            <label>
              Target Drive Path
              <input name="targetDrivePath" value={form.targetDrivePath} onChange={handleChange} />
            </label>
            <label>
              Archive Name
              <input name="archiveName" value={form.archiveName} onChange={handleChange} />
            </label>
            <label>
              Format
              <select name="archiveFormat" value={form.archiveFormat} onChange={handleChange}>
                <option value="zip">ZIP</option>
                <option value="tar">TAR</option>
                <option value="gztar">TAR.GZ</option>
                <option value="bztar">TAR.BZ2</option>
                <option value="xztar">TAR.XZ</option>
              </select>
            </label>
          </div>
        )}
        {error && <div className="error">{error}</div>}
        <button className="btn-primary" onClick={handleStart}>Start Download</button>
      </div>

      {currentTask && (
        <div className="task-status">
          <h3>Status: {currentTask.status}</h3>
          <progress value={currentTask.progress || 0} max="100" />
          <div>{Math.round(currentTask.progress || 0)}%</div>
          <button className="btn-secondary" onClick={() => cancelTask(currentTask.taskId)}>Cancel</button>
        </div>
      )}
    </div>
  );
}
