import React, { useContext, useState } from 'react';
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
      <h2>Archive Model</h2>
      <div className="form-section">
        <label>
          Source Folder
          <input name="sourceFolderPath" value={form.sourceFolderPath} onChange={handleChange} />
        </label>
        <label>
          Target Drive
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
        {error && <div className="error">{error}</div>}
        <button onClick={handleStart}>Start</button>
      </div>
      {currentTask && (
        <div className="task-status">
          <h3>Status: {currentTask.status}</h3>
          <progress value={currentTask.progress || 0} max="100" />
          <div>{Math.round(currentTask.progress || 0)}%</div>
          <button onClick={() => cancelTask(currentTask.taskId)}>Cancel</button>
        </div>
      )}
    </div>
  );
}
