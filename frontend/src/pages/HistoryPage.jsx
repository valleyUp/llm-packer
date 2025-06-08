import React, { useContext } from 'react';
import {
  Clock,
  Download,
  Archive,
  CheckCircle,
  XCircle,
  Loader,
  Calendar,
  Activity
} from 'lucide-react';
import { TaskContext } from '../TaskContext';

const getStatusIcon = (status) => {
  switch (status) {
    case 'completed':
      return <CheckCircle className="status-icon success" />;
    case 'failed':
    case 'error':
      return <XCircle className="status-icon error" />;
    case 'running':
    case 'downloading':
    case 'archiving':
      return <Loader className="status-icon running animate-spin" />;
    default:
      return <Clock className="status-icon pending" />;
  }
};

const getStatusColor = (status) => {
  switch (status) {
    case 'completed':
      return 'success';
    case 'failed':
    case 'error':
      return 'error';
    case 'running':
    case 'downloading':
    case 'archiving':
      return 'running';
    default:
      return 'pending';
  }
};

export default function HistoryPage() {
  const { history } = useContext(TaskContext);

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-icon">
          <Clock />
        </div>
        <div>
          <h2>Task History</h2>
          <p>View and manage your download and archive task history.</p>
        </div>
      </div>

      {history.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">
            <Activity />
          </div>
          <h3>No Tasks Yet</h3>
          <p>Your download and archive history will appear here once you start using the application.</p>
        </div>
      ) : (
        <div className="history-grid">
          {history.map(task => (
            <div key={task.taskId} className={`history-card ${getStatusColor(task.status)}`}>
              <div className="history-header">
                <div className="task-type">
                  {task.type === 'archive' ? <Archive /> : <Download />}
                  <span>{task.type === 'archive' ? 'Archive' : 'Download'}</span>
                </div>
                {getStatusIcon(task.status)}
              </div>

              <div className="history-content">
                <h4>{task.modelId || task.archiveName || 'Unknown Task'}</h4>
                <div className="task-meta">
                  <div className="meta-item">
                    <Calendar />
                    <span>{new Date(task.createdAt || Date.now()).toLocaleDateString()}</span>
                  </div>
                  <div className="meta-item">
                    <Activity />
                    <span>Status: {task.status}</span>
                  </div>
                </div>
              </div>

              <div className="history-progress">
                <div className="progress-bar small">
                  <div
                    className="progress-fill"
                    style={{ width: `${task.progress || 0}%` }}
                  ></div>
                </div>
                <span className="progress-label">{Math.round(task.progress || 0)}%</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
