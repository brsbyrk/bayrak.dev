/**
 * Derive src/data/posts.json from blog/*.mdx front matter.
 *
 * Why this exists: the blog list is no longer the homepage, and the blog plugin
 * does not expose a list hook for a custom page. So the front matter is read
 * once at build time (npm `prebuild`/`prestart`) and handed to the homepage as
 * data. One source (the .mdx files), one derivation (this file), one consumer.
 *
 * It refuses to finish if a post has no absolute /blog/ slug or if the count it
 * wrote disagrees with the number of .mdx files: a silent off-by-one here would
 * ship a homepage missing a post.
 */
import fs from 'node:fs';
import path from 'node:path';
import matter from 'gray-matter';

const BLOG = path.resolve('blog');
const OUT = path.resolve('src/data/posts.json');

const files = fs.readdirSync(BLOG).filter((f) => f.endsWith('.mdx')).sort();
const posts = [];

for (const file of files) {
  const raw = fs.readFileSync(path.join(BLOG, file), 'utf8');
  const {data} = matter(raw);
  // The blog plugin composes permalink = routeBasePath + slug, so the slug here
  // is the post's own name ('/<name>') and '/blog' comes from the config. A slug
  // that still carried '/blog/' would publish at /blog/blog/<name>.
  const slug = String(data.slug ?? '');
  if (!slug.startsWith('/') || slug.startsWith('/blog/')) {
    console.error(`ABORT — ${file} has slug '${slug}', expected '/<name>' (no /blog/ prefix)`);
    process.exit(1);
  }
  if (!data.date || !data.title) {
    console.error(`ABORT — ${file} is missing date or title`);
    process.exit(1);
  }
  const date = new Date(data.date);
  posts.push({
    file,
    title: String(data.title),
    permalink: `/blog${slug}`.replace(/\/$/, ''),
    date: date.toISOString().slice(0, 10),
    dateLabel: date.toLocaleDateString('en-US', {year: 'numeric', month: 'short', day: 'numeric', timeZone: 'UTC'}),
    description: data.description ? String(data.description) : '',
    tags: Array.isArray(data.tags) ? data.tags.map(String) : [],
  });
}

posts.sort((a, b) => (a.date < b.date ? 1 : -1));

if (posts.length !== files.length) {
  console.error(`ABORT — parsed ${posts.length} of ${files.length} files`);
  process.exit(1);
}

fs.mkdirSync(path.dirname(OUT), {recursive: true});
fs.writeFileSync(OUT, JSON.stringify({generatedAt: new Date().toISOString(), posts}, null, 2) + '\n');
console.log(`gen-site-data: ${posts.length} posts -> ${path.relative(process.cwd(), OUT)}`);
