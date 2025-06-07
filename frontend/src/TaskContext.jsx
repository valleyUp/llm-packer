import React, { createContext, useState, useEffect, useCallback } from 'react';
import { api } from './api';

export const TaskContext = createContext(null);

export function TaskProvider({ children }) {
  const [currentTask, setCurrentTask] = useState(null);
  const [history, setHistory] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('taskHistory')) || [];
    } catch {
      return [];
    }
  });
  const [pollingId, setPollingId] = useState(null);

  const saveHistory = (list) => {
    setHistory(list);
    try { localStorage.setItem('taskHistory', JSON.stringify(list)); } catch {}
  };

  const updateHistory = (task) => {
    saveHistory([task, ...history.filter(t => t.taskId !== task.taskId)].slice(0,10));
  };

  const stopPolling = useCallback(() => {
    if (pollingId) clearInterval(pollingId);
    setPollingId(null);
  }, [pollingId]);

  const pollTask = useCallback((taskId) => {
    stopPolling();
    const id = setInterval(async () => {
      try {
        const data = await api.getTaskStatus(taskId);
        setCurrentTask(data);
        updateHistory(data);
        if (['completed','failed','cancelled'].includes(data.status)) {
          stopPolling();
        }
      } catch {
        stopPolling();
      }
    }, 1000);
    setPollingId(id);
  }, [stopPolling, history]);

  const startDownload = async(params) => {
    const data = await api.startDownload(params);
    setCurrentTask(data);
    updateHistory(data);
    pollTask(data.taskId);
    return data;
  };

  const archiveModel = async(params) => {
    const data = await api.archiveModel(params);
    setCurrentTask(data);
    updateHistory(data);
    pollTask(data.taskId);
    return data;
  };

  const cancelTask = async(taskId) => {
    await api.cancelTask(taskId);
    stopPolling();
  };

  const value = { currentTask, history, startDownload, archiveModel, cancelTask };
  return <TaskContext.Provider value={value}>{children}</TaskContext.Provider>;
}
