import React, { useEffect, useRef, useState } from 'react';
import './Hero.css';

// Profile photo - will be imported after placing photo in assets
let profilePhoto = null;
try {
  profilePhoto = new URL('../assets/profile.jpg', import.meta.url).href;
} catch (e) {
  profilePhoto = null;
}

const roles = [
  'AI & Machine Learning Engineer',
  'Python Developer',
  'Data Analyst',
  'Problem Solver',
  'AI Enthusiast',
];

function ParticleCanvas() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    let animId;

    const resize = () => {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    const particles = Array.from({ length: 80 }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      r: Math.random() * 2 + 0.5,
      opacity: Math.random() * 0.5 + 0.1,
    }));

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      particles.forEach((p) => {
        p.x += p.vx;
        p.y += p.vy;
        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(99, 102, 241, ${p.opacity})`;
        ctx.fill();
      });

      // Draw connections
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 120) {
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.strokeStyle = `rgba(99, 102, 241, ${0.08 * (1 - dist / 120)})`;
            ctx.lineWidth = 0.8;
            ctx.stroke();
          }
        }
      }

      animId = requestAnimationFrame(draw);
    };

    draw();
    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', resize);
    };
  }, []);

  return <canvas ref={canvasRef} className="particle-canvas" />;
}

function TypeWriter({ texts }) {
  const [display, setDisplay] = useState('');
  const [textIdx, setTextIdx] = useState(0);
  const [charIdx, setCharIdx] = useState(0);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const current = texts[textIdx];
    let timeout;

    if (!deleting && charIdx < current.length) {
      timeout = setTimeout(() => setCharIdx(c => c + 1), 60);
    } else if (!deleting && charIdx === current.length) {
      timeout = setTimeout(() => setDeleting(true), 2000);
    } else if (deleting && charIdx > 0) {
      timeout = setTimeout(() => setCharIdx(c => c - 1), 35);
    } else if (deleting && charIdx === 0) {
      setDeleting(false);
      setTextIdx(i => (i + 1) % texts.length);
    }

    setDisplay(current.slice(0, charIdx));
    return () => clearTimeout(timeout);
  }, [charIdx, deleting, textIdx, texts]);

  return (
    <span className="typewriter">
      {display}
      <span className="cursor">|</span>
    </span>
  );
}

export default function Hero() {
  return (
    <section id="home" className="hero">
      <ParticleCanvas />

      {/* Background Gradient Orbs */}
      <div className="hero-orb orb-1" />
      <div className="hero-orb orb-2" />
      <div className="hero-orb orb-3" />

      <div className="container hero-inner">
        <div className="hero-content" data-aos="fade-right">
          {/* Status Badge */}
          <div className="status-badge">
            <span className="status-dot" />
            Available for Opportunities
          </div>

          {/* Greeting */}
          <p className="hero-greeting">Hello, I'm</p>

          {/* Name */}
          <h1 className="hero-name">
            <span className="gradient-text">Arivazhagan</span>
            <br />
            <span className="hero-surname">Sundarraj</span>
          </h1>

          {/* Role */}
          <div className="hero-role">
            <TypeWriter texts={roles} />
          </div>

          {/* Description */}
          <p className="hero-desc">
            Aspiring <strong>AI & Machine Learning Engineer</strong> with strong foundations in 
            Python, data analysis, and model development. Passionate about solving real-world 
            problems using intelligent systems.
          </p>

          {/* Stats */}
          <div className="hero-stats">
            <div className="stat-item">
              <span className="stat-number">5+</span>
              <span className="stat-label">Certifications</span>
            </div>
            <div className="stat-divider" />
            <div className="stat-item">
              <span className="stat-number">2+</span>
              <span className="stat-label">Projects</span>
            </div>
            <div className="stat-divider" />
            <div className="stat-item">
              <span className="stat-number">AI</span>
              <span className="stat-label">Specialized</span>
            </div>
          </div>

          {/* CTA Buttons */}
          <div className="hero-cta">
            <a href="#projects" className="btn-primary" onClick={e => { e.preventDefault(); document.getElementById('projects').scrollIntoView({behavior:'smooth'}); }}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
              </svg>
              View Projects
            </a>
            <a href="https://mail.google.com/mail/?view=cm&to=arivazhaganarivu0611@gmail.com" target="_blank" rel="noopener noreferrer" className="btn-outline">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                <polyline points="22,6 12,13 2,6"/>
              </svg>
              Contact Me
            </a>
          </div>

          {/* Social Links */}
          <div className="hero-social">
            <a href="https://www.linkedin.com/in/arivazhagan-sundarraj-862004394" target="_blank" rel="noopener noreferrer" className="social-link" aria-label="LinkedIn">
              <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                <path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6zM2 9h4v12H2z"/>
                <circle cx="4" cy="4" r="2"/>
              </svg>
            </a>
            <a href="https://github.com/arivazhagansundarraj" target="_blank" rel="noopener noreferrer" className="social-link" aria-label="GitHub">
              <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0 1 12 6.844a9.59 9.59 0 0 1 2.504.337c1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.02 10.02 0 0 0 22 12.017C22 6.484 17.522 2 12 2z"/>
              </svg>
            </a>
            <a href="https://mail.google.com/mail/?view=cm&to=arivazhaganarivu0611@gmail.com" target="_blank" rel="noopener noreferrer" className="social-link" aria-label="Email">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="20" height="20">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                <polyline points="22,6 12,13 2,6"/>
              </svg>
            </a>
            <a href="tel:9363278239" className="social-link" aria-label="Phone">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="20" height="20">
                <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12a19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 3.6 1.18h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L7.91 8.9a16 16 0 0 0 6.08 6.08l1.08-.9a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>
              </svg>
            </a>
          </div>
        </div>

        {/* Profile Photo */}
        <div className="hero-photo-wrapper" data-aos="fade-left">
          <div className="photo-frame">
            <div className="photo-glow" />
            <div className="photo-ring ring-1" />
            <div className="photo-ring ring-2" />
            <div className="photo-container">
              {profilePhoto ? (
                <img src={profilePhoto} alt="Arivazhagan Sundarraj" className="profile-photo" />
              ) : (
                <div className="profile-photo-placeholder">
                  <svg viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ width: '100%', height: '100%' }}>
                    <rect width="200" height="200" fill="rgba(99,102,241,0.05)"/>
                    <circle cx="100" cy="80" r="35" fill="rgba(99,102,241,0.3)"/>
                    <ellipse cx="100" cy="160" rx="55" ry="40" fill="rgba(99,102,241,0.2)"/>
                    <text x="100" y="108" textAnchor="middle" fill="rgba(99,102,241,0.8)" fontSize="28" fontFamily="Space Grotesk" fontWeight="800">AS</text>
                  </svg>
                </div>
              )}
            </div>
            {/* Floating badges */}
            <div className="float-badge badge-1">
              <span>🤖</span> AI Engineer
            </div>
            <div className="float-badge badge-2">
              <span>🐍</span> Python
            </div>
            <div className="float-badge badge-3">
              <span>📊</span> ML Models
            </div>
          </div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <div className="scroll-indicator">
        <div className="scroll-mouse">
          <div className="scroll-wheel" />
        </div>
        <span>Scroll Down</span>
      </div>
    </section>
  );
}
