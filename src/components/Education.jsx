import React from 'react';
import './Education.css';

const educationData = [
  {
    id: 1,
    institution: 'RVS College of Arts & Science',
    location: 'Sulur, Coimbatore',
    degree: "Bachelor's in AI & Machine Learning",
    period: '2023 – 2027',
    percentage: '72%',
    status: 'Ongoing',
    icon: '🎓',
    color: '#6366f1',
    highlights: ['AI & ML Core Modules', 'Data Science', 'Python Programming', 'Research Projects'],
  },
  {
    id: 2,
    institution: 'Government Boys Higher Sec School',
    location: 'Tiruppur',
    degree: 'Higher Secondary Certificate (HSC)',
    period: '2021 – 2023',
    percentage: '70.33%',
    status: 'Completed',
    icon: '📚',
    color: '#06b6d4',
    highlights: ['Mathematics', 'Computer Science', 'Physics', 'Chemistry'],
  },
  {
    id: 3,
    institution: 'Government Boys Higher Sec School',
    location: 'Tiruppur',
    degree: 'Secondary School Leaving Certificate (SSLC)',
    period: '2019 – 2021',
    percentage: '80%',
    status: 'Completed',
    icon: '🏫',
    color: '#10b981',
    highlights: ['Mathematics', 'Science', 'Social Studies', 'Languages'],
  },
];

export default function Education() {
  return (
    <section id="education" className="section education-section">
      <div className="container">
        <div className="section-header">
          <span className="section-label">Background</span>
          <h2 className="section-title">
            My <span className="gradient-text">Education</span>
          </h2>
          <p className="section-subtitle">
            A strong academic foundation building toward expertise in AI and Machine Learning.
          </p>
        </div>

        {/* Timeline */}
        <div className="education-timeline">
          {educationData.map((edu, index) => (
            <div key={edu.id} className="edu-item" style={{ '--edu-color': edu.color }}>
              {/* Timeline Line */}
              <div className="timeline-line">
                <div className="timeline-dot" style={{ background: edu.color, boxShadow: `0 0 15px ${edu.color}60` }}>
                  <span>{edu.icon}</span>
                </div>
                {index < educationData.length - 1 && (
                  <div className="timeline-connector" style={{ background: `linear-gradient(to bottom, ${edu.color}40, ${educationData[index + 1].color}40)` }} />
                )}
              </div>

              {/* Card */}
              <div className="edu-card">
                {/* Header */}
                <div className="edu-card-header">
                  <div className="edu-main">
                    <h3 className="edu-institution">{edu.institution}</h3>
                    <p className="edu-location">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                        <circle cx="12" cy="10" r="3"/>
                      </svg>
                      {edu.location}
                    </p>
                  </div>
                  <div className="edu-score" style={{ background: `${edu.color}12`, borderColor: `${edu.color}25` }}>
                    <span className="score-number" style={{ color: edu.color }}>{edu.percentage}</span>
                    <span className="score-label">Score</span>
                  </div>
                </div>

                {/* Degree */}
                <p className="edu-degree">{edu.degree}</p>

                {/* Period & Status */}
                <div className="edu-meta">
                  <div className="edu-period">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10"/>
                      <polyline points="12 6 12 12 16 14"/>
                    </svg>
                    {edu.period}
                  </div>
                  <span
                    className={`edu-status ${edu.status === 'Ongoing' ? 'ongoing' : 'completed'}`}
                  >
                    {edu.status === 'Ongoing' && <span className="status-dot-anim" />}
                    {edu.status}
                  </span>
                </div>

                {/* Highlights */}
                <div className="edu-highlights">
                  {edu.highlights.map((h, i) => (
                    <span key={i} className="edu-highlight" style={{ borderColor: `${edu.color}20`, color: '#94a3b8' }}>
                      {h}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
