import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import useGlobalData from '@docusaurus/useGlobalData';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import styles from './index.module.css';

function Hero() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <section className={styles.hero}>
      <div className={styles.heroContent}>
        <h1 className={styles.name}>{siteConfig.title}</h1>
        <p className={styles.tagline}>software engineer &bull; systems &bull; tools</p>
        <p className={styles.bio}>
          I build systems with Rust, design tools, explore ideas, and
          write about what I learn along the way.
        </p>
        <div className={styles.socials}>
          <a href="https://github.com/brsbyrk" target="_blank" rel="noopener noreferrer" className={styles.socialIcon} aria-label="GitHub">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.468-2.38 1.235-3.22-.123-.3-.535-1.52.117-3.16 0 0 1.008-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.29-1.552 3.297-1.23 3.297-1.23.653 1.653.24 2.873.118 3.176.77.84 1.233 1.91 1.233 3.22 0 4.61-2.803 5.62-5.475 5.92.43.37.824 1.102.824 2.222 0 1.606-.015 2.896-.015 3.286 0 .322.216.694.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/>
            </svg>
          </a>
          <a href="https://www.linkedin.com/in/barisbayrak/" target="_blank" rel="noopener noreferrer" className={styles.socialIcon} aria-label="LinkedIn">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
            </svg>
          </a>
          <a href="https://x.com/bbarisbayrak" target="_blank" rel="noopener noreferrer" className={styles.socialIcon} aria-label="X">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
            </svg>
          </a>
          <a href="mailto:baris@bayrak.dev" className={styles.socialIcon} aria-label="Email">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 4H2a2 2 0 00-2 2v12a2 2 0 002 2h20a2 2 0 002-2V6a2 2 0 00-2-2zm0 2v.01L12 13 2 6V6l10 7 10-7V6z"/>
            </svg>
          </a>
        </div>
      </div>
    </section>
  );
}

function BlogPosts({posts}) {
  if (!posts || posts.length === 0) return null;

  return (
    <section className={styles.posts}>
      <h2 className={styles.sectionTitle}>Latest Writing</h2>
      <div className={styles.postList}>
        {posts.slice(0, 3).map((post) => {
          const {metadata} = post;
          const date = new Date(metadata.date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
          });
          return (
            <Link to={metadata.permalink} key={metadata.permalink} className={styles.postCard}>
              <div className={styles.postMeta}>
                <time className={styles.postDate}>{date}</time>
                {metadata.tags?.length > 0 && (
                  <span className={styles.postTags}>
                    {metadata.tags.map(t => t.label).join(', ')}
                  </span>
                )}
              </div>
              <h3 className={styles.postTitle}>{metadata.title}</h3>
              <p className={styles.postDesc}>{metadata.description}</p>
            </Link>
          );
        })}
      </div>
      <Link to="/blog" className={styles.allPosts}>All posts →</Link>
    </section>
  );
}

export default function Home() {
  const globalData = useGlobalData();
  const blogPlugin = globalData?.['docusaurus-plugin-content-blog']?.default;
  const posts = blogPlugin?.posts;

  return (
    <Layout
      title="Baris Bayrak"
      description="Thoughts and ideas by Baris Bayrak">
      <main className={styles.page}>
        <Hero />
        <BlogPosts posts={posts} />
      </main>
    </Layout>
  );
}
