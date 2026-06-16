import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import styles from './index.module.css';

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={siteConfig.title}
      description="Thoughts and ideas by Baris Bayrak">
      <main className={styles.main}>
        <div className={styles.hero}>
          <h1 className={styles.name}>{siteConfig.title}</h1>
          <p className={styles.tagline}>{siteConfig.tagline}</p>
          <p className={styles.bio}>
            Building systems with Rust, designing tools, exploring ideas.
            I write about projects, engineering, and things I'm learning.
          </p>
          <div className={styles.links}>
            <Link to="/blog" className={styles.link}>Blog →</Link>
            <Link to="/about" className={styles.link}>About →</Link>
          </div>
        </div>
      </main>
    </Layout>
  );
}
