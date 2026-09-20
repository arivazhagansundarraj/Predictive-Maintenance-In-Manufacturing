import React, { useState } from 'react';
import './Internships.css';

const internshipData = [
  {
    id: 'nts-internship',
    title: 'Python with Generative AI',
    type: 'Internship',
    organization: 'Net Tel Solutions (NTS)',
    location: 'Coimbatore, India',
    period: '28 Aug 2026 – 14 Sep 2026',
    icon: '⚡',
    color: '#8b5cf6',
    image: '/certs/cert_net_tel.png',
    certNo: 'QMS/AC60/0425',
    description: 'Completed hands-on Internship Training focused on Python development, Large Language Models (LLMs), prompt engineering, and building Generative AI applications.',
    highlights: ['Python', 'Generative AI', 'LLMs', 'Prompt Engineering', 'AI Application Dev'],
    badge: 'ISO 9001 Certified',
  },
  {
    id: 'internshala-ml',
    title: 'Machine Learning with AI',
    type: 'Traineeship',
    organization: 'Internshala Trainings & IITM Pravartak',
    location: 'Online Training',
    period: 'Jul 2026 – Sep 2026 (8 Weeks)',
    icon: '🤖',
    color: '#06b6d4',
    image: '/certs/cert_internshala.png',
    certNo: 'nt86xlx50n_',
    verifyUrl: 'https://trainings.internshala.com/view_certificate/btmzuv7zq1m/nt86xlx50n_/',
    description: '8-week intensive training program covering Supervised & Unsupervised Learning, Data Analytics with Python, and AI Lifecycle Management Tools. Recognized as a Top Performer.',
    highlights: ['Machine Learning', 'Data Analytics', 'Python', 'Supervised Learning', 'AI Lifecycle Tools', 'Top Performer'],
    badge: 'Top Performer',
  },
];

/* ── Modal Lightbox Component ── */
function InternModal({ item, onClose }) {
  const [imgError, setImgError] = useState(false);

  React.useEffect(() => {
    const handler = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onClose]);

  return (
    <div className="intern-modal-overlay" onClick={onClose}>
      <div className="intern-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="intern-modal-header" style={{ borderColor: `${item.color}40` }}>
          <div className="intern-modal-title-wrap">
            <span className="intern-modal-icon">{item.icon}</span>
            <div>
              <span className="intern-modal-type" style={{ color: item.color }}>
                {item.type} · {item.organization}
              </span>
              <h3 className="intern-modal-title">{item.title}</h3>
              <p className="intern-modal-meta">{item.period} · {item.location}</p>
            </div>
          </div>
          <button className="intern-modal-close" onClick={onClose} aria-label="Close">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" width="20" height="20">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        {/* Certificate Image Body */}
        <div className="intern-modal-body">
          {!imgError ? (
            <img
              src={item.image}
              alt={item.title}
              className="intern-modal-img"
              onError={() => setImgError(true)}
            />
          ) : (
            <div className="intern-modal-fallback" style={{ borderColor: `${item.color}30` }}>
              <span style={{ fontSize: '60px' }}>{item.icon}</span>
              <p style={{ color: '#94a3b8', marginTop: '16px', textAlign: 'center' }}>
                Certificate document display fallback.
              </p>
            </div>
          )}
        </div>

        {/* Footer actions */}
        <div className="intern-modal-footer">
          <div
            className="intern-verified-badge"
            style={{ color: item.color, borderColor: `${item.color}30`, background: `${item.color}10` }}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/>
            </svg>
            Verified Certificate
          </div>

          <div className="intern-modal-actions">
            {item.verifyUrl && (
              <a
                href={item.verifyUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="intern-verify-btn"
                style={{ borderColor: `${item.color}50`, color: item.color }}
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                  <polyline points="15 3 21 3 21 9"/>
                  <line x1="10" y1="14" x2="21" y2="3"/>
                </svg>
                Verify Online
              </a>
            )}
            {!imgError && (
              <a
                href={item.image}
                download
                className="intern-download-btn"
                style={{ background: `linear-gradient(135deg, ${item.color}cc, ${item.color})` }}
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
    </div>
  );
}

/* ── Main Component ── */
export default function Internships() {
  const [activeItem, setActiveItem] = useState(null);

  return (
    <section id="internships" className="section internships-section">
      <div className="container">
        {/* Section Header */}
        <div className="section-header">
          <span className="section-label">Experience</span>
          <h2 className="section-title">
            Internships &amp; <span className="gradient-text">Traineeships</span>
          </h2>
          <p className="section-subtitle">
            Hands-on professional experience and intensive training programs in AI, Machine Learning, and Generative AI.
          </p>
        </div>

        {/* Grid layout */}
        <div className="internships-grid">
          {internshipData.map((item, index) => (
            <div
              key={item.id}
              className="intern-card"
              style={{ '--card-color': item.color, animationDelay: `${index * 0.15}s` }}
            >
              {/* Top accent line */}
              <div className="intern-card-accent" style={{ background: item.color }} />

              {/* Header row */}
              <div className="intern-card-header">
                <div
                  className="intern-icon-wrap"
                  style={{ background: `${item.color}15`, borderColor: `${item.color}30` }}
                >
                  <span>{item.icon}</span>
                </div>
                <div className="intern-card-meta">
                  <span className="intern-type-pill" style={{ color: item.color, borderColor: `${item.color}30`, background: `${item.color}10` }}>
                    {item.type}
                  </span>
                  {item.badge && (
                    <span className="intern-badge-pill" style={{ borderColor: `${item.color}25` }}>
                      {item.badge}
                    </span>
                  )}
                </div>
              </div>

              {/* Card Content */}
              <h3 className="intern-card-title">{item.title}</h3>
              <p className="intern-org">{item.organization}</p>
              <p className="intern-period">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12 6 12 12 16 14"/>
                </svg>
                {item.period}
              </p>

              <p className="intern-desc">{item.description}</p>

              {/* Skill Tags */}
              <div className="intern-tags">
                {item.highlights.map((tag, i) => (
                  <span key={i} className="intern-tag" style={{ borderColor: `${item.color}20` }}>
                    {tag}
                  </span>
                ))}
              </div>

              {/* Action Buttons */}
              <div className="intern-card-footer">
                <button
                  className="intern-view-btn"
                  style={{ '--btn-color': item.color }}
                  onClick={() => setActiveItem(item)}
                >
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                  Show Certificate
                </button>

                {item.verifyUrl && (
                  <a
                    href={item.verifyUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="intern-direct-verify"
                    title="Verify Certificate Online"
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                      <polyline points="15 3 21 3 21 9"/>
                      <line x1="10" y1="14" x2="21" y2="3"/>
                    </svg>
                    Verify Link
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Modal Lightbox */}
      {activeItem && (
        <InternModal item={activeItem} onClose={() => setActiveItem(null)} />
      )}
    </section>
  );
}
