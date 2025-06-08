import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { Download, Archive, Clock, Info } from 'lucide-react';
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
      // Calculate position to center the indicator under each tab
      const tabWidth = 100 / routes.length; // 25% for 4 tabs
      const indicatorWidth = tabWidth - 2; // Slightly smaller for better visual
      const left = (tabWidth * index) + 1; // Add 1% offset for centering

      setIndicatorStyle({
        left: `${left}%`,
        width: `${indicatorWidth}%`
      });
    }
  }, [location]);

  return (
    <div className="app-container">
      <nav className="app-nav">
        <div className="nav-tabs">
          <Link to="/" className={location.pathname === '/' ? 'active' : ''}>
            <Download />
            Download
          </Link>
          <Link to="/archive" className={location.pathname === '/archive' ? 'active' : ''}>
            <Archive />
            Archive
          </Link>
          <Link to="/history" className={location.pathname === '/history' ? 'active' : ''}>
            <Clock />
            History
          </Link>
          <Link to="/about" className={location.pathname === '/about' ? 'active' : ''}>
            <Info />
            About
          </Link>
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
