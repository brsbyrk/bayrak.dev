// @ts-check
import {themes as prismThemes} from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Baris Bayrak',
  tagline: 'software engineer',
  favicon: 'img/baris-scan-192x192.png',

  future: {
    v4: true,
  },

  url: 'https://bayrak.dev',
  baseUrl: '/',

  organizationName: 'brsbyrk',
  projectName: 'bayrak.dev',

  onBrokenLinks: 'throw',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  plugins: [
    [
      '@docusaurus/plugin-client-redirects',
      {
        // Two post-URL shapes are dead. Every post first published at
        // /<year>/<month>/<day>/<slug>, then briefly at /writing/<slug>, and now
        // lives at /blog/<slug>. The real 301s are at the web server (one Caddy
        // regex per dead shape, see ~/services/sites/caddy/Caddyfile); these
        // entries keep the static build self-consistent when it is served
        // without Caddy in front of it.
        redirects: [
          // the original dated URLs
          { from: '/2026/06/30/carnot-compression-research', to: '/blog/carnot-compression-research/' },
          { from: '/2026/07/30/carnot-gpu-rans', to: '/blog/carnot-gpu-rans/' },
          { from: '/2026/09/12/carnot-graph-routing', to: '/blog/carnot-graph-routing/' },
          { from: '/2026/09/16/flyos-connectome-retention', to: '/blog/flyos-connectome-retention/' },
          { from: '/2026/09/17/taalas-etched-model-silicon', to: '/blog/taalas-etched-model-silicon/' },
          { from: '/2026/09/22/claimaudit-three-ceilings-no-buyer', to: '/blog/claimaudit-three-ceilings-no-buyer/' },
          { from: '/2026/09/24/openjev-nine-reimplementations-refusal-test', to: '/blog/openjev-nine-reimplementations-refusal-test/' },
          // the short-lived /writing/ prefix
          { from: '/writing/carnot-compression-research', to: '/blog/carnot-compression-research/' },
          { from: '/writing/carnot-gpu-rans', to: '/blog/carnot-gpu-rans/' },
          { from: '/writing/carnot-graph-routing', to: '/blog/carnot-graph-routing/' },
          { from: '/writing/flyos-connectome-retention', to: '/blog/flyos-connectome-retention/' },
          { from: '/writing/taalas-etched-model-silicon', to: '/blog/taalas-etched-model-silicon/' },
          { from: '/writing/claimaudit-three-ceilings-no-buyer', to: '/blog/claimaudit-three-ceilings-no-buyer/' },
          { from: '/writing/openjev-nine-reimplementations-refusal-test', to: '/blog/openjev-nine-reimplementations-refusal-test/' },
        ],
      },
    ],
  ],

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: false,
        blog: {
          routeBasePath: '/',
          // Note: `permalink` is NOT a blog option in Docusaurus v3 (the build
          // fails with '"permalink" is not allowed'), and routeBasePath cannot
          // move because with no src/pages the blog IS the homepage. The URL
          // is routeBasePath + the post's slug, and for a dated filename like
          // 2026-09-24-name.mdx the plugin expands the date into the slug
          // (blogUtils.js parseBlogFileName). So each post carries an explicit
          // `slug: /writing/<name>` in its front matter instead.
          showReadingTime: true,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
          editUrl: 'https://github.com/brsbyrk/bayrak.dev/tree/main/',
          onInlineTags: 'warn',
          onInlineAuthors: 'warn',
          onUntruncatedBlogPosts: 'warn',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      image: 'img/baris-scan-512x512.png',
      colorMode: {
        defaultMode: 'light',
        disableSwitch: false,
        respectPrefersColorScheme: true,
      },
      navbar: {
        title: 'Baris Bayrak',
        hideOnScroll: true,
        items: [
          {to: '/about', label: 'About', position: 'right'},
        ],
      },
      footer: {
        style: 'light',
        links: [
          {
            items: [
              {label: 'GitHub', href: 'https://github.com/brsbyrk'},
              {label: 'LinkedIn', href: 'https://www.linkedin.com/in/barisbayrak/'},
              {label: 'X', href: 'https://x.com/bbarisbayrak'},
              {label: 'Email', href: 'mailto:baris@bayrak.dev'},
            ],
          },
        ],
        copyright: `© ${new Date().getFullYear()} Baris Bayrak`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
    }),
};

export default config;
