import React from 'react';
import './Projects.css';

const projects = [
  {
    id: 1,
    name: 'Customer Churn Prediction',
    tagline: 'Machine Learning & Customer Analytics',
    description: 'An end-to-end Machine Learning model predicting customer churn, identifying key retention factors, and empowering business decisions to prevent customer attrition.',
    tags: ['Python', 'Machine Learning', 'Customer Churn', 'Scikit-Learn', 'Data Analytics'],
    icon: '📉',
    color: '#6366f1',
    gradient: 'linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.08))',
    features: ['Churn Risk Modeling', 'Customer Behavioral Insights', 'Predictive Analytics', 'Retention Strategy'],
    status: 'Completed',
    githubUrl: 'https://github.com/arivazhagansundarraj/Customer-Churn-Prediction',
    liveUrl: null,
  },
  {
    id: 2,
    name: 'Mail Spam Detection',
    tagline: 'NLP & Machine Learning Security Guard',
    description: 'An intelligent Natural Language Processing (NLP) classifier that detects and filters spam emails in real-time, featuring an interactive Streamlit web application.',
    tags: ['Python', 'Streamlit', 'NLP', 'Machine Learning', 'Spam Classifier'],
    icon: '📧',
    color: '#06b6d4',
    gradient: 'linear-gradient(135deg, rgba(6, 182, 212, 0.15), rgba(99, 102, 241, 0.08))',
    features: ['Real-Time Spam Filtering', 'NLP Text Preprocessing', 'Streamlit Web UI', 'High Classification Accuracy'],
    status: 'Completed',
    githubUrl: 'https://github.com/arivazhagansundarraj/Mail_Spam_detection',
    liveUrl: 'https://mailspamdetection-guard.streamlit.app/',
  },
  {
    id: 3,
    name: 'Predictive Maintenance in Manufacturing',
    tagline: 'Industrial AI & IoT Failure Forecasting',
    description: 'An industrial Machine Learning solution forecasting equipment failure before downtime occurs, optimizing maintenance schedules and reducing operational costs.',
    tags: ['Python', 'Streamlit', 'Predictive Maintenance', 'IoT & ML', 'Industrial AI'],
    icon: '⚙️',
    color: '#f59e0b',
    gradient: 'linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(16, 185, 129, 0.08))',
    features: ['Equipment Failure Prediction', 'Downtime & Cost Reduction', 'Interactive Streamlit App', 'Sensor Data Analytics'],
    status: 'Completed',
    githubUrl: 'https://github.com/arivazhagansundarraj/Predictive-Maintenance-In-Manufacturing',
    liveUrl: 'https://predictive-maintenance-in-manufacturing.streamlit.app/',
  },
];

function ProjectCard({ project, index }) {
  return (
    <div
      className="project-card"
      style={{
        '--card-color': project.color,
        '--card-gradient': project.gradient,
        animationDelay: `${index * 0.2}s`,
      }}
    >
      {/* Top Bar */}
      <div className="project-card-top">
        <div className="project-icon" style={{ background: project.gradient, borderColor: `${project.color}30` }}>
          <span>{project.icon}</span>
        </div>
        <div className="project-status">
          <span className="status-dot-green" />
          {project.status}
        </div>
      </div>

      {/* Content */}
      <div className="project-content">
        <h3 className="project-name">{project.name}</h3>
        <p className="project-tagline" style={{ color: project.color }}>{project.tagline}</p>
        <p className="project-desc">{project.description}</p>
      </div>

      {/* Features */}
      <div className="project-features">
        {project.features.map((f, i) => (
          <span key={i} className="project-feature">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
            {f}
          </span>
        ))}
      </div>

      {/* Tags */}
      <div className="project-tags">
        {project.tags.map((tag, i) => (
          <span key={i} className="project-tag" style={{ borderColor: `${project.color}25`, color: project.color }}>
            {tag}
          </span>
        ))}
      </div>

      {/* Action Links */}
      <div className="project-links">
        {project.githubUrl && (
          <a
            href={project.githubUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="project-link-btn github-link"
            aria-label="GitHub Repository"
          >
            <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
              <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0 1 12 6.844a9.59 9.59 0 0 1 2.504.337c1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.02 10.02 0 0 0 22 12.017C22 6.484 17.522 2 12 2z"/>
            </svg>
            GitHub
          </a>
        )}

        {project.liveUrl && (
          <a
            href={project.liveUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="project-link-btn live-link"
            style={{ '--btn-color': project.color }}
            aria-label="Live Streamlit App"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
              <polyline points="15 3 21 3 21 9"/>
              <line x1="10" y1="14" x2="21" y2="3"/>
            </svg>
            Live App
          </a>
        )}
      </div>

      {/* Hover Glow */}
      <div className="project-glow" style={{ background: `radial-gradient(circle at 50% 100%, ${project.color}15, transparent 70%)` }} />
    </div>
  );
}

export default function Projects() {
  return (
    <section id="projects" className="section projects-section">
      <div className="container">
        <div className="section-header">
          <span className="section-label">Portfolio</span>
          <h2 className="section-title">
            Featured <span className="gradient-text">Projects</span>
          </h2>
          <p className="section-subtitle">
            Real-world Machine Learning &amp; AI applications — featuring live interactive web deployments and open-source code.
          </p>
        </div>

        <div className="projects-grid">
          {projects.map((project, index) => (
            <ProjectCard key={project.id} project={project} index={index} />
          ))}
        </div>

        {/* Extra Activities */}
        <div className="extra-activities">
          <h3 className="extra-title">
            <span className="gradient-text">Extra Curricular</span> Activities
          </h3>
          <div className="activities-grid">
            <div className="activity-card">
              <div className="activity-icon">🤖</div>
              <div className="activity-content">
                <h4>Arduino Radar Project</h4>
                <p>Science Exhibition Participant — Built an Arduino-based radar system demonstrating real-time object detection.</p>
                <div className="activity-meta">
                  <span>RVS College of Arts &amp; Science</span>
                  <span className="activity-year">2025</span>
                </div>
              </div>
            </div>
            <div className="activity-card">
              <div className="activity-icon">🤟</div>
              <div className="activity-content">
                <h4>SignSpeak AI Project</h4>
                <p>YII '2026 Participant — Developed an AI-powered sign language recognition system to bridge communication gaps.</p>
                <div className="activity-meta">
                  <span>RVS College of Arts &amp; Science</span>
                  <span className="activity-year">2026</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
