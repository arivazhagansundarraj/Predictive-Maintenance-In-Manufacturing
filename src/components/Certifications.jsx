import React, { useState } from 'react';
import './Certifications.css';

// Images go in: public/certs/  (e.g. public/certs/cert_hp_life.jpg)
// Referenced as /certs/filename — Vite serves public/ as root, no imports needed
const certifications = [
  {
    id: 1,
    title: 'AI for Business Professionals',
    issuer: 'HP Life',
    year: '2025',
    icon: '🧠',
    color: '#6366f1',
    category: 'Artificial Intelligence',
    image: '/certs/cert_hp_life.jpg',
  },
  {
    id: 2,
    title: 'Website UI/UX Designing using ChatGPT',
    issuer: 'Simplilearn SkillUP',
    year: '2026',
    icon: '🎨',
    color: '#06b6d4',
    category: 'Design & Development',
    image: '/certs/cert_simplilearn.jpg',
  },
  {
    id: 3,
    title: 'Micro Local Rag Beginners',
    issuer: 'FreeAcademy.ai',
    year: '2026',
    icon: '🎮',
    color: '#f59e0b',
    category: 'Community & Technology',
    image: '/certs/cert_rog.jpg',
  },
  {
    id: 4,
    title: 'Projects on Power BI',
    issuer: 'Infosys SpringBoard',
    year: '2026',
    icon: '📊',
    color: '#10b981',
    category: 'Data Analytics',
    image: '/certs/cert_infosys.jpg',
  },
];

/* ── Modal Lightbox ── */
function CertModal({ cert, onClose }) {
  const [imgError, setImgError] = useState(false);

  // Close on Escape key
  React.useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onClose]);

  return (
    <div className="cert-modal-overlay" onClick={onClose}>
      <div className="cert-modal" onClick={(e) => e.stopPropagation()}>

        {/* Header */}
        <div className="cert-modal-header" style={{ borderColor: `${cert.color}40` }}>
          <div className="cert-modal-title-wrap">
            <span className="cert-modal-icon">{cert.icon}</span>
            <div>
              <span className="cert-modal-category" style={{ color: cert.color }}>
                {cert.category}
              </span>
              <h3 className="cert-modal-title">{cert.title}</h3>
              <p className="cert-modal-issuer">{cert.issuer} · {cert.year}</p>
            </div>
          </div>
          <button className="cert-modal-close" onClick={onClose} aria-label="Close">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" width="20" height="20">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        {/* Certificate Image */}
        <div className="cert-modal-body">
          {!imgError ? (
            <img
              src={cert.image}
              alt={cert.title}
              className="cert-modal-img"
              onError={() => setImgError(true)}
            />
          ) : (
            <div className="cert-modal-fallback" style={{ borderColor: `${cert.color}30` }}>
              <span style={{ fontSize: '60px' }}>{cert.icon}</span>
              <p style={{ color: '#64748b', marginTop: '16px', textAlign: 'center', lineHeight: 1.7 }}>
                Certificate image not added yet.<br />
                Copy your certificate image to:<br />
                <code>Portfolio\public\certs\{cert.image.split('/').pop()}</code>
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="cert-modal-footer">
          <div
            className="cert-verified-badge"
            style={{ color: cert.color, borderColor: `${cert.color}30`, background: `${cert.color}10` }}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/>
            </svg>
            Verified Certificate
          </div>
          {!imgError && (
            <a
              href={cert.image}
              download
              className="cert-download-btn"
              style={{ background: `linear-gradient(135deg, ${cert.color}cc, ${cert.color})` }}
            >
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              Download
            </a>
          )}
        </div>

      </div>
    </div>
  );
}

/* ── Cert Card ── */
function CertCard({ cert, index, onView }) {
  return (
    <div
      className="cert-card"
      style={{ '--cert-color': cert.color, animationDelay: `${index * 0.15}s` }}
    >
      <div className="cert-accent-bar" style={{ background: cert.color }} />

      <div className="cert-icon-wrap" style={{ background: `${cert.color}12`, borderColor: `${cert.color}25` }}>
        <span className="cert-icon">{cert.icon}</span>
      </div>

      <div className="cert-content">
        <span className="cert-category" style={{ color: cert.color }}>{cert.category}</span>
        <h3 className="cert-title">{cert.title}</h3>
        <div className="cert-meta">
          <div className="cert-issuer">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z"/>
              <path d="M2 17l10 5 10-5"/>
              <path d="M2 12l10 5 10-5"/>
            </svg>
            {cert.issuer}
          </div>
          <div className="cert-year" style={{ color: cert.color }}>{cert.year}</div>
        </div>

        <button
          className="cert-view-btn"
          style={{ '--btn-color': cert.color }}
          onClick={() => onView(cert)}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
            <circle cx="12" cy="12" r="3"/>
          </svg>
          Show Certificate
        </button>
      </div>

      <div className="cert-verified">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/>
        </svg>
        Verified
      </div>
    </div>
  );
}

/* ── Main Section ── */
export default function Certifications() {
  const [activeCert, setActiveCert] = useState(null);

  return (
    <section id="certifications" className="section certifications-section">
      <div className="container">
        <div className="section-header">
          <span className="section-label">Credentials</span>
          <h2 className="section-title">
            My <span className="gradient-text">Certifications</span>
          </h2>
          <p className="section-subtitle">
            Industry-recognized credentials from leading technology companies and platforms.
          </p>
        </div>

        <div className="cert-grid">
          {certifications.map((cert, index) => (
            <CertCard key={cert.id} cert={cert} index={index} onView={setActiveCert} />
          ))}
        </div>

        {/* Hobbies & Languages Row */}
        <div className="extras-row">
          <div className="extras-card">
            <h3 className="extras-heading"><span className="gradient-text">Hobbies</span></h3>
            <div className="hobbies-grid">
              <div className="hobby-chip-wrap">
                <div className="hobby-chip">
                  <span>🎮</span>Gaming
                </div>
                <ul className="hobby-sublist">
                  <li>🎯 Battle Ground Mobile India</li>
                  <li>📖 Story Games</li>
                  <li>🖥️ PC Games</li>
                </ul>
              </div>
              <div className="hobby-chip-wrap">
                <div className="hobby-chip">
                  <span>🌿</span>Gardening
                </div>
                <ul className="hobby-sublist hobby-sublist--green">
                  <li>🌱 Planting and watering plants</li>
                  <li>🌾 Removing weeds and preparing soil</li>
                  <li>✂️ Pruning and maintaining the garden</li>
                </ul>
              </div>
              <div className="hobby-chip-wrap">
                <div className="hobby-chip">
                  <span>✈️</span>Travelling
                </div>
                <ul className="hobby-sublist hobby-sublist--cyan">
                  <li>🗺️ Exploring new places and cultures</li>
                  <li>💬 Communication skills through travel experiences</li>
                  <li>🔄 Building adaptability</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="extras-card">
            <h3 className="extras-heading"><span className="gradient-text">Languages</span></h3>
            <div className="languages-list">
              {[
                { lang: 'Tamil', level: 'Native', percent: 100 },
                { lang: 'English', level: 'Proficient', percent: 85 },
                { lang: 'Malayalam', level: 'Conversational', percent: 70 },
              ].map((l) => (
                <div key={l.lang} className="lang-item">
                  <div className="lang-header">
                    <span className="lang-name">{l.lang}</span>
                    <span className="lang-level">{l.level}</span>
                  </div>
                  <div className="lang-bar">
                    <div className="lang-fill" style={{ width: `${l.percent}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Modal — rendered outside container so it covers full screen */}
      {activeCert && (
        <CertModal cert={activeCert} onClose={() => setActiveCert(null)} />
      )}
    </section>
  );
}
