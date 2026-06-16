import React from 'react';

export function Highlight({children, color}) {
  return (
    <span
      style={{
        backgroundColor: color || '#60a5fa',
        borderRadius: '4px',
        color: '#fff',
        padding: '0.2rem 0.4rem',
        fontWeight: 600,
      }}>
      {children}
    </span>
  );
}

export function Info({title, children}) {
  return (
    <div
      style={{
        backgroundColor: 'var(--ifm-color-info-contrast-background)',
        borderLeft: '4px solid var(--ifm-color-info-dark)',
        borderRadius: '6px',
        padding: '0.8rem 1rem',
        margin: '1rem 0',
      }}>
      {title && <strong>{title}</strong>}
      <div>{children}</div>
    </div>
  );
}

export function ProjectCard({name, description, link}) {
  return (
    <div
      style={{
        border: '1px solid var(--ifm-color-emphasis-300)',
        borderRadius: '8px',
        padding: '1.2rem',
        margin: '1rem 0',
      }}>
      <h3 style={{margin: 0}}>
        <a href={link} target="_blank" rel="noopener noreferrer">
          {name}
        </a>
      </h3>
      <p style={{margin: '0.5rem 0 0'}}>{description}</p>
    </div>
  );
}
