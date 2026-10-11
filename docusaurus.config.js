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
        // Every post moved from /<year>/<month>/<day>/<slug> to /writing/<slug>/.
        // These are 301s, so existing links — and whatever signal the dated URLs
        // accumulated — carry over instead of dying.
        redirects: [
          { from: '/2026/06/30/carnot-compression-research', to: '/writing/carnot-compression-research/' },
          { from: '/2026/07/30/carnot-gpu-rans', to: '/writing/carnot-gpu-rans/' },
          { from: '/2026/09/12/carnot-graph-routing', to: '/writing/carnot-graph-routing/' },
          { from: '/2026/09/16/flyos-connectome-retention', to: '/writing/flyos-connectome-retention/' },
          { from: '/2026/09/17/taalas-etched-model-silicon', to: '/writing/taalas-etched-model-silicon/' },
          { from: '/2026/09/22/claimaudit-three-ceilings-no-buyer', to: '/writing/claimaudit-three-ceilings-no-buyer/' },
          { from: '/2026/09/24/openjev-nine-reimplementations-refusal-test', to: '/writing/openjev-nine-reimplementations-refusal-test/' },
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
