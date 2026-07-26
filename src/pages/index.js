import useGlobalData from '@docusaurus/useGlobalData';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import styles from './index.module.css';

function Posts({posts}) {
  if (!posts || posts.length === 0) {
    return <p className={styles.empty}>No posts yet.</p>;
  }

  return (
    <ol className={styles.list}>
      {posts.map((post) => {
        const {metadata} = post;
        const date = new Date(metadata.date).toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
        });
        return (
          <li key={metadata.permalink} className={styles.item}>
            <time className={styles.date}>{date}</time>
            <div className={styles.body}>
              <Link to={metadata.permalink} className={styles.title}>
                {metadata.title}
              </Link>
              {metadata.tags?.length > 0 && (
                <span className={styles.tags}>
                  {metadata.tags.map(t => t.label).join(', ')}
                </span>
              )}
            </div>
          </li>
        );
      })}
    </ol>
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
        <header className={styles.header}>
          <h1 className={styles.name}>Baris Bayrak</h1>
          <p className={styles.bio}>
            Software engineer. I build systems, explore ideas, and
            write about what I learn.
          </p>
        </header>
        <Posts posts={posts} />
      </main>
    </Layout>
  );
}
