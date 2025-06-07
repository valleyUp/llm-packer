import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import DownloadPage from './pages/DownloadPage';
import ArchivePage from './pages/ArchivePage';
import HistoryPage from './pages/HistoryPage';
import AboutPage from './pages/AboutPage';
import './styles.css';

export default function App() {
  const location = useLocation();
  const [indicatorStyle, setIndicatorStyle] = useState({ left: '0%' });

  useEffect(() => {
    const routes = ['/', '/archive', '/history', '/about'];
    const index = routes.indexOf(location.pathname);
    if (index !== -1) {
      const width = 25;
      setIndicatorStyle({ left: `${width * index}%`, width: `${width}%` });
    }
  }, [location]);

  return (
    <div className="app-container">
      <header className="app-header">
        <h1 className="app-title">LLM Weights Downloader</h1>
      </header>
      <nav className="app-nav">
        <div className="nav-tabs">
          <Link to="/" className={location.pathname === '/' ? 'active' : ''}>Download</Link>
          <Link to="/archive" className={location.pathname === '/archive' ? 'active' : ''}>Archive</Link>
          <Link to="/history" className={location.pathname === '/history' ? 'active' : ''}>History</Link>
          <Link to="/about" className={location.pathname === '/about' ? 'active' : ''}>About</Link>
          <div className="nav-indicator" style={indicatorStyle} />
        </div>
      </nav>
      <main className="app-content">
        <Routes>
          <Route path="/" element={<DownloadPage />} />
          <Route path="/archive" element={<ArchivePage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/about" element={<AboutPage />} />
        </Routes>
      </main>
      <footer className="app-footer">© {new Date().getFullYear()} LLM Weights Downloader</footer>
    </div>
  );
}
