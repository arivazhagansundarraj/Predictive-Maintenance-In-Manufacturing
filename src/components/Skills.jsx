import React, { useRef, useEffect, useState } from 'react';
import './Skills.css';

const skillCategories = [
  {
    id: 'technical',
    label: 'Technical Skills',
    icon: '💻',
    color: '#6366f1',
    skills: [
      { name: 'Python', level: 80, icon: '🐍' },
      { name: 'ETL', level: 85, icon: '⚙️' },
      { name: 'MySQL', level: 85, icon: '🗄️' },
      { name: 'Deep Learning', level: 60, icon: '🤖' },
      { name: 'GenAI', level: 60, icon: '✨' },
    ],
  },
  {
    id: 'tools',
    label: 'Tools & IDEs',
    icon: '🛠️',
    color: '#06b6d4',
    skills: [
      { name: 'VS Code', level: 90, icon: '📝' },
      { name: 'GitHub', level: 80, icon: '🐙' },
      { name: 'Power BI', level: 72, icon: '📈' },
      { name: 'MS Office', level: 85, icon: '📋' },
    ],
  },
  {
    id: 'soft',
    label: 'Soft Skills',
    icon: '🧠',
    color: '#f59e0b',
    skills: [
      { name: 'Leadership', level: 80, icon: '👑' },
      { name: 'Presentation', level: 85, icon: '🎤' },
      { name: 'Teamwork', level: 90, icon: '🤝' },
      { name: 'Adaptability', level: 88, icon: '⚡' },
      { name: 'DB Management', level: 75, icon: '🗄️' },
    ],
  },
];

const techPills = [
  'Python', 'Machine Learning', 'Artificial Intelligence', 'Data Analysis',
  'ETL', 'MySQL', 'Deep Learning', 'GenAI', 'Power BI', 'GitHub',
  'VS Code', 'TensorFlow', 'Data Science', 'Gen AI', 'Model Development',
];

function SkillBar({ name, level, color, icon, index }) {
  const [width, setWidth] = useState(0);
  const ref = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setTimeout(() => setWidth(level), index * 80);
        }
      },
      { threshold: 0.3 }
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [level, index]);

  return (
    <div className="skill-bar-item" ref={ref}>
      <div className="skill-bar-header">
        <span className="skill-name">
          {icon && (
            <span
              className="skill-icon-badge"
              style={{
                background: `linear-gradient(135deg, ${color}22, ${color}44)`,
                border: `1px solid ${color}40`,
                boxShadow: `0 0 8px ${color}30`,
              }}
            >
              {icon}
            </span>
          )}
          {name}
        </span>
        <span className="skill-percent" style={{ color }}>{level}%</span>
      </div>
      <div className="skill-bar-track">
        <div
          className="skill-bar-fill"
          style={{
            width: `${width}%`,
            background: `linear-gradient(90deg, ${color}70, ${color})`,
            boxShadow: `0 0 8px ${color}40`,
          }}
        />
      </div>
    </div>
  );
}

export default function Skills() {
  const [activeTab, setActiveTab] = useState('technical');

  const active = skillCategories.find(c => c.id === activeTab);

  return (
    <section id="skills" className="section skills-section">
      <div className="container">
        {/* Header */}
        <div className="section-header">
          <span className="section-label">Expertise</span>
          <h2 className="section-title">
            My <span className="gradient-text">Skills</span>
          </h2>
          <p className="section-subtitle">
            A comprehensive toolkit built through hands-on projects, certifications, and continuous learning.
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="skills-tabs">
          {skillCategories.map(cat => (
            <button
              key={cat.id}
              className={`skills-tab ${activeTab === cat.id ? 'active' : ''}`}
              onClick={() => setActiveTab(cat.id)}
              style={{ '--tab-color': cat.color }}
            >
              <span>{cat.icon}</span>
              {cat.label}
            </button>
          ))}
        </div>

        {/* Skills Grid */}
        <div className="skills-content">
          <div className="skills-bars">
            {active.skills.map((skill, i) => (
              <SkillBar
                key={skill.name}
                {...skill}
                color={active.color}
                index={i}
              />
            ))}
          </div>

          {/* Visual Decoration */}
          <div className="skills-visual">
            <div className="skills-circle-wrap">
              {/* Colored ring circle — border color matches active tab */}
              <div
                className="skills-circle"
                style={{
                  borderColor: active.color,
                  boxShadow: `0 0 30px ${active.color}30, inset 0 0 30px ${active.color}10`,
                }}
              >
                <div className="skills-circle-inner">
                  {/* Category icon with gradient glow */}
                  <span
                    className="skills-circle-icon"
                    style={{ filter: `drop-shadow(0 0 14px ${active.color}90)` }}
                  >
                    {active.icon}
                  </span>
                  <span className="skills-circle-label" style={{ color: active.color }}>
                    {active.label}
                  </span>
                  <span className="skills-circle-count">{active.skills.length} Skills</span>
                </div>
              </div>
              {/* Orbit scattered icons REMOVED */}
            </div>
          </div>
        </div>

        {/* Tech Pills */}
        <div className="tech-pills-section">
          <p className="tech-pills-label">Technologies & Tools</p>
          <div className="tech-pills-scroll">
            <div className="tech-pills-track">
              {[...techPills, ...techPills].map((pill, i) => (
                <span key={i} className="tech-pill">{pill}</span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
