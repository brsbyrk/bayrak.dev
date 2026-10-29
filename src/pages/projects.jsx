import React from 'react';
import Layout from '@theme/Layout';
import projectsData from '@site/src/data/projects.json';
import styles from './site.module.css';

// Status is literal. "public" means a stranger can open the source; the entry
// then links to it. Anything else says so, and links only to what exists.
function Project({project}) {
  const {name, languages, description, status, repo, writeups} = project;
  return (
    <div className={styles.projRow}>
      <div>
        <div className={styles.workHead}>
          <span className={styles.workName}>{name}</span>
          <span className={styles.workLangs}>{languages.join(' · ')}</span>
        </div>
        <p className={styles.workDesc}>{description}</p>
      </div>
      <span className={status === 'public' ? `${styles.status} ${styles.statusOpen}` : styles.status}>
        {status}
      </span>
      <p className={styles.projLinks}>
        {repo && (
          <a href={repo} target="_blank" rel="noopener noreferrer">
            source ↗
          </a>
        )}
        {writeups.map((w) => (
          <a key={w.href} href={w.href}>
            {w.label}
          </a>
        ))}
        {!repo && writeups.length === 0 && <span>closed source, no public write-up yet</span>}
      </p>
    </div>
  );
}

export default function Projects() {
  const projects = projectsData.projects;
  return (
    <Layout
      title="Projects"
      description="What I build: compression research, a metasearch library, knowledge infrastructure for agents, and a decision layer for game NPCs.">
      <div className={styles.wrap}>
        <h1 className={styles.statement} style={{fontSize: 'clamp(26px,3.2vw,34px)'}}>
          Projects
        </h1>
        <p className={styles.sub}>
          Each description is the project&rsquo;s own. Status is literal: <strong>public</strong> means
          you can open or install it; <strong>in development</strong> means the source is closed and
          the entry links only to what exists.
        </p>
        <div style={{marginTop: 46}}>
          <div className={styles.rule} />
          {projects.map((project) => (
            <Project key={project.name} project={project} />
          ))}
        </div>
      </div>
    </Layout>
  );
}
