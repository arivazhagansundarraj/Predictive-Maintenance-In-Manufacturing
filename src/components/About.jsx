import React from 'react';
import './About.css';

let profilePhoto = null;
try {
  profilePhoto = new URL('../assets/profile.jpg', import.meta.url).href;
} catch (e) {
  profilePhoto = null;
}

const highlights = [
  { icon: '🎓', label: 'Education', value: "B.Sc. AI & ML", sub: 'RVS College, Sulur' },
  { icon: '📍', label: 'Location', value: 'Tiruppur', sub: 'Tamil Nadu, India' },
  { icon: '🌐', label: 'Languages', value: 'Tamil, English', sub: 'Malayalam' },
  { icon: '💡', label: 'Interests', value: 'AI, ML, Data', sub: 'Research & Innovation' },
];

export default function About() {
  return (
    <section id="about" className="section about-section">
      <div className="container">
        <div className="about-grid">
          {/* Photo Side */}
          <div className="about-photo-wrap">
            <div className="about-photo-frame">
              {/* Single clean clip container — overflow:hidden keeps image inside border-radius */}
              <div className="about-photo-clip">
                {profilePhoto ? (
                  <img src={profilePhoto} alt="Arivazhagan Sundarraj" className="about-photo" />
                ) : (
                  <div className="about-photo-fallback">🧑‍💻</div>
                )}
              </div>
              {/* Objective card overlay */}
              <div className="about-obj-card">
                <span className="obj-label">Career Objective</span>
                <p className="obj-text">
                  Aspiring AI & ML Engineer solving real-world problems with intelligent systems.
                </p>
              </div>
            </div>
          </div>

          {/* Content Side */}
          <div className="about-content">
            <span className="section-label">About Me</span>
            <h2 className="section-title">
              Building the Future with <span className="gradient-text">Intelligence</span>
            </h2>

            <p className="about-para">
              I'm <strong>Arivazhagan Sundarraj</strong>, an aspiring AI & Machine Learning engineer 
              currently pursuing my Bachelor's in AI and ML at RVS College of Arts & Science, Sulur. 
              I'm passionate about creating intelligent systems that solve real-world challenges.
            </p>

            <p className="about-para">
              With a strong foundation in <strong>Python</strong>, <strong>data analysis</strong>, and 
              <strong> model development</strong>, I've worked on exciting projects ranging from 
              e-commerce platforms to AI-powered sign language recognition systems.
            </p>

            {/* Highlights Grid */}
            <div className="about-highlights">
              {highlights.map((h, i) => (
                <div key={i} className="highlight-chip">
                  <span className="highlight-icon">{h.icon}</span>
                  <div>
                    <span className="highlight-label">{h.label}</span>
                    <span className="highlight-value">{h.value}</span>
                    <span className="highlight-sub">{h.sub}</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Objective Full */}
            <div className="about-objective">
              <div className="obj-header">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="18" height="18">
                  <circle cx="12" cy="12" r="10"/>
                  <path d="M12 8v4l3 3"/>
                </svg>
                Career Objective
              </div>
              <p>
                Focused on solving real-world problems using intelligent systems. Passionate about 
                innovation, continuous learning, and applying AI techniques to develop efficient, 
                scalable solutions in academic and project environments.
              </p>
            </div>

            <div className="about-cta">
              <a href="https://mail.google.com/mail/?view=cm&to=arivazhaganarivu0611@gmail.com" target="_blank" rel="noopener noreferrer" className="btn-primary">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="18" height="18">
                  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                  <polyline points="22,6 12,13 2,6"/>
                </svg>
                Get In Touch
              </a>
              <a href="https://www.linkedin.com/in/arivazhagan-sundarraj-862004394" target="_blank" rel="noopener noreferrer" className="btn-outline">
                <svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
                  <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6zM2 9h4v12H2z"/>
                  <circle cx="4" cy="4" r="2"/>
                </svg>
                LinkedIn Profile
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
