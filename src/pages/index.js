import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import useGlobalData from '@docusaurus/useGlobalData';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import styles from './index.module.css';

function Hero() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <section className={styles.hero}>
      <h1 className={styles.name}>{siteConfig.title}</h1>
      <p className={styles.tagline}>
        software engineer &bull; systems &bull; tools
      </p>
      <p className={styles.bio}>
        I build systems with Rust, design tools, explore ideas, and
        write about what I learn along the way.
      </p>
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
