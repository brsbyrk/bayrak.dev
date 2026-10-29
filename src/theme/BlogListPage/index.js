import React from 'react';
import clsx from 'clsx';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import {
  PageMetadata,
  HtmlClassNameProvider,
  ThemeClassNames,
} from '@docusaurus/theme-common';
import BlogLayout from '@theme/BlogLayout';
import BlogPostItems from '@theme/BlogPostItems';
import BlogListPageStructuredData from '@theme/BlogListPage/StructuredData';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';

function BlogListPageMetadata(props) {
  const {metadata} = props;
  const {
    siteConfig: {title: siteTitle},
  } = useDocusaurusContext();
  const {blogDescription, blogTitle, permalink} = metadata;
  const isBlogOnlyMode = permalink === '/';
  const title = isBlogOnlyMode ? siteTitle : blogTitle;
  return (
    <>
      <PageMetadata title={title} description={blogDescription} />
    </>
  );
}

// The blog no longer owns '/', so this page is only ever the /blog/ index. The
// homepage has its own copy and its own page (src/pages/index.jsx); keeping a
// second bio here would be a duplicate to drift.
function SectionHeader() {
  return (
    <header className={styles.header}>
      <h1 className={styles.name}>Writing</h1>
      <p className={styles.bio}>
        Long-form notes: what I built, what I measured, and what failed.
      </p>
      <p className={styles.bio}>
        <Link to="/blog/archive">Archive</Link> · <Link to="/blog/tags">Tags</Link>
      </p>
    </header>
  );
}

function BlogListPageContent(props) {
  const {items} = props;

  return (
    <BlogLayout>
      <SectionHeader />
      <BlogPostItems items={items} />
    </BlogLayout>
  );
}

export default function BlogListPage(props) {
  return (
    <HtmlClassNameProvider
      className={clsx(
        ThemeClassNames.wrapper.blogPages,
        ThemeClassNames.page.blogListPage,
      )}>
      <BlogListPageMetadata {...props} />
      <BlogListPageStructuredData {...props} />
      <BlogListPageContent {...props} />
    </HtmlClassNameProvider>
  );
}
