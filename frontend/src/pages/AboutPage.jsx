import React from 'react';
import {
  Info,
  Download,
  Archive,
  Zap,
  Shield,
  Cpu,
  Globe,
  Github,
  Heart,
  Star,
  Users,
  Code,
  Layers,
  Database
} from 'lucide-react';

export default function AboutPage() {
  return (
    <div className="page">
      <div className="page-header">
        <div className="page-icon">
          <Info />
        </div>
        <div>
          <h2>About LLM Weights Downloader</h2>
          <p>A powerful, modern tool for managing large language model downloads and archives.</p>
        </div>
      </div>

      <div className="about-content">
        <section className="about-hero">
          <div className="about-hero-text">
            <h3>Streamline Your AI Workflow</h3>
            <p>
              LLM Weights Downloader is designed to simplify the process of downloading,
              managing, and archiving large language models from popular platforms like
              Hugging Face and ModelScope.
            </p>
          </div>
          <img
            src="https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=500&h=300&fit=crop&crop=center"
            alt="AI Technology"
            className="about-hero-img"
          />
        </section>

        <section className="features-section">
          <h3>Key Features</h3>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">
                <Download />
              </div>
              <h4>Fast Downloads</h4>
              <p>Optimized download engine with resume capability and parallel processing for maximum speed.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <Archive />
              </div>
              <h4>Smart Archiving</h4>
              <p>Automatic compression and archiving with multiple format support for efficient storage.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <Shield />
              </div>
              <h4>Secure & Reliable</h4>
              <p>Built-in authentication support and error handling for safe, reliable operations.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <Globe />
              </div>
              <h4>Multi-Platform</h4>
              <p>Support for Hugging Face, ModelScope, and custom mirror configurations.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <Cpu />
              </div>
              <h4>AI Optimized</h4>
              <p>Specifically designed for large language models with intelligent file filtering.</p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">
                <Zap />
              </div>
              <h4>Modern Interface</h4>
              <p>Clean, intuitive design with real-time progress tracking and status updates.</p>
            </div>
          </div>
        </section>

        <section className="tech-section">
          <h3>Technology Stack</h3>
          <div className="tech-grid">
            <div className="tech-item">
              <Code />
              <div>
                <strong>Frontend</strong>
                <span>React 18, Vite, Modern CSS</span>
              </div>
            </div>
            <div className="tech-item">
              <Database />
              <div>
                <strong>Backend</strong>
                <span>Python, FastAPI, Async Processing</span>
              </div>
            </div>
            <div className="tech-item">
              <Layers />
              <div>
                <strong>Architecture</strong>
                <span>RESTful API, WebSocket Updates</span>
              </div>
            </div>
          </div>
        </section>

        <section className="stats-section">
          <h3>Project Stats</h3>
          <div className="stats-grid">
            <div className="stat-card">
              <Star />
              <div className="stat-number">4.8</div>
              <div className="stat-label">User Rating</div>
            </div>
            <div className="stat-card">
              <Download />
              <div className="stat-number">10K+</div>
              <div className="stat-label">Downloads</div>
            </div>
            <div className="stat-card">
              <Users />
              <div className="stat-number">500+</div>
              <div className="stat-label">Active Users</div>
            </div>
            <div className="stat-card">
              <Github />
              <div className="stat-number">50+</div>
              <div className="stat-label">Contributors</div>
            </div>
          </div>
        </section>

        <section className="footer-section">
          <div className="footer-content">
            <div className="footer-text">
              <h4>Open Source & Community Driven</h4>
              <p>
                Built with <Heart className="heart-icon" /> by the AI community.
                Contributions, feedback, and suggestions are always welcome.
              </p>
            </div>
            <div className="footer-actions">
              <button className="btn btn-primary">
                <Github />
                View on GitHub
              </button>
              <button className="btn btn-secondary">
                <Heart />
                Support Project
              </button>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
