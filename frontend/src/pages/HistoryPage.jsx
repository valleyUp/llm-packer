import React, { useContext } from 'react';
import { TaskContext } from '../TaskContext';

export default function HistoryPage() {
  const { history } = useContext(TaskContext);
  return (
    <div className="page">
      <h2>Task History</h2>
      {history.length === 0 && <p>No tasks yet.</p>}
      {history.map(t => (
        <div key={t.taskId} className="history-item">
          <div>{t.type === 'archive' ? 'Archive' : 'Download'} - {t.modelId || t.archiveName}</div>
          <div>Status: {t.status}</div>
          <div>Progress: {Math.round(t.progress || 0)}%</div>
        </div>
      ))}
    </div>
  );
}
