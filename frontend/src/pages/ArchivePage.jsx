import React, { useContext, useState } from 'react';
import {
  Archive,
  FolderOpen,
  HardDrive,
  Package,
  AlertCircle,
  Loader,
  CheckCircle
} from 'lucide-react';
import { TaskContext } from '../TaskContext';

export default function ArchivePage() {
  const { currentTask, archiveModel, cancelTask } = useContext(TaskContext);
  const [form, setForm] = useState({
    sourceFolderPath: '',
    targetDrivePath: '',
    archiveName: '',
    archiveFormat: 'zip'
  });
  const [error, setError] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  const handleStart = async () => {
    try {
      await archiveModel(form);
    } catch {
      setError('Failed to start archive');
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-icon">
          <Archive />
        </div>
        <div>
          <h2>Archive Model</h2>
          <p>Compress and store your downloaded models for efficient storage and backup.</p>
        </div>
      </div>

      <div className="form-section">
        <div className="form-row">
          <div className="form-group">
            <label>
              Source Folder
              <div className="input-group">
                <FolderOpen />
                <input
                  name="sourceFolderPath"
                  value={form.sourceFolderPath}
                  onChange={handleChange}
                  className="with-icon"
                  placeholder="/path/to/model/folder"
                />
              </div>
            </label>
          </div>
          <div className="form-group">
            <label>
              Target Drive
              <div className="input-group">
                <HardDrive />
                <input
                  name="targetDrivePath"
                  value={form.targetDrivePath}
                  onChange={handleChange}
                  className="with-icon"
                  placeholder="/path/to/backup/drive"
                />
              </div>
            </label>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>
              Archive Name
              <div className="input-group">
                <Package />
                <input
                  name="archiveName"
                  value={form.archiveName}
                  onChange={handleChange}
                  className="with-icon"
                  placeholder="my-model-backup"
                />
              </div>
            </label>
          </div>
          <div className="form-group">
            <label>
              Archive Format
              <select name="archiveFormat" value={form.archiveFormat} onChange={handleChange} className="select-with-emoji">
                <option value="zip">📦 ZIP (Fast, Compatible)</option>
                <option value="tar">📄 TAR (Uncompressed)</option>
                <option value="gztar">🗜️ TAR.GZ (Good Compression)</option>
                <option value="bztar">🗜️ TAR.BZ2 (Better Compression)</option>
                <option value="xztar">🗜️ TAR.XZ (Best Compression)</option>
              </select>
            </label>
          </div>
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
            disabled={!form.sourceFolderPath || !form.targetDrivePath || !form.archiveName}
          >
            <Archive />
            Start Archiving
          </button>
        </div>
      </div>

      {currentTask && (
        <div className="task-status-card">
          <div className="task-header">
            <div className="task-info">
              <h3>Archiving in Progress</h3>
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
              <Package />
              <span>Archive: {currentTask.archiveName || 'Processing...'}</span>
            </div>
            <div className="detail-item">
              <Archive />
              <span>Format: {currentTask.archiveFormat || 'zip'}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
