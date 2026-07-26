import React from 'react';
import {BlogPostProvider, useBlogPost} from '@docusaurus/plugin-content-blog/client';
import BlogPostItem from '@theme/BlogPostItem';
import styles from './styles.module.css';

function CompactPostItem({children}) {
  const {metadata} = useBlogPost();
  const date = new Date(metadata.date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });

  return (
    <article className={styles.item}>
      <time className={styles.date}>{date}</time>
      <a href={metadata.permalink} className={styles.title}>
        {metadata.title}
      </a>
    </article>
  );
}

export default function BlogPostItems({items, component: BlogPostItemComponent}) {
  if (BlogPostItemComponent) {
    return (
      <>
        {items.map(({content: BlogPostContent}) => (
          <BlogPostProvider
            key={BlogPostContent.metadata.permalink}
            content={BlogPostContent}>
            <BlogPostItemComponent>
              <BlogPostContent />
            </BlogPostItemComponent>
          </BlogPostProvider>
        ))}
      </>
    );
  }

  return (
    <>
      {items.map(({content: BlogPostContent}) => (
        <BlogPostProvider
          key={BlogPostContent.metadata.permalink}
          content={BlogPostContent}>
          <CompactPostItem>
            <BlogPostContent />
          </CompactPostItem>
        </BlogPostProvider>
      ))}
    </>
  );
}
