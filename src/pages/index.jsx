import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import postsData from '@site/src/data/posts.json';
import projectsData from '@site/src/data/projects.json';
import styles from './site.module.css';

// The rail is a deliberate choice, not "all projects": four entries, each of
// which either has a public repo or says plainly that it does not.
const RAIL = ['carnot', 'dizin', 'pliny', 'ethogram'];

function WorkRow({project}) {
  const {name, languages, summary, repo, writeups} = project;
  return (
    <div className={styles.workRow}>
      <div className={styles.workHead}>
        <span className={styles.workName}>{name}</span>
        <span className={styles.workLangs}>{languages.join(' · ')}</span>
      </div>
      <p className={styles.workDesc}>{summary}</p>
      <p className={styles.workMeta}>
        {repo ? (
          <a href={repo} target="_blank" rel="noopener noreferrer">
            public repo ↗
          </a>
        ) : (
          <span>in development · closed source</span>
        )}
        {repo && writeups.length > 0 && ` · ${writeups.length} write-ups`}
      </p>
    </div>
  );
}

export default function Home() {
  const posts = postsData.posts;
  const rail = RAIL.map((n) => projectsData.projects.find((p) => p.name === n)).filter(Boolean);

  return (
    <Layout
      title="Baris Bayrak"
      description="Systems engineer. Compression, retrieval and simulation in Rust and Python — with the measurements published, including the ones that went against me.">
      <div className={styles.wrap}>
        <h1 className={styles.statement}>
          I build systems, then I measure whether they <em>actually</em> work.
        </h1>
        <p className={styles.sub}>
          Rust and Python — compression, retrieval, simulation. The write-ups carry their method,
          the negative results, and the claims I had to retract.
        </p>

        <div className={styles.cols}>
          <section>
            <h2 className={styles.label}>Writing</h2>
            <div className={styles.rule} />
            {posts.map((post) => (
              <Link className={styles.postRow} key={post.permalink} to={post.permalink}>
                <span className={styles.postTitle}>{post.title}</span>
                <span className={styles.date}>{post.dateLabel}</span>
              </Link>
            ))}
            <Link className={styles.more} to="/blog">
              All writing →
            </Link>
          </section>

          <section>
            <h2 className={styles.label}>Selected work</h2>
            <div className={styles.rule} />
            {rail.map((project) => (
              <WorkRow key={project.name} project={project} />
            ))}
            <Link className={styles.more} to="/projects">
              All projects →
            </Link>
          </section>
        </div>
      </div>
    </Layout>
  );
}
