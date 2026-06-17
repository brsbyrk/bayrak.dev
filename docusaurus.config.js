// @ts-check
import {themes as prismThemes} from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Baris Bayrak',
  tagline: 'software engineer',
  favicon: 'img/favicon.ico',

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

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: false,
        blog: {
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
        logo: {
          alt: 'Baris Bayrak',
          src: 'img/logo.png',
        },
        items: [
          {to: '/blog', label: 'Blog', position: 'left'},
          {to: '/about', label: 'About', position: 'left'},
          {
            href: 'https://github.com/brsbyrk',
            position: 'right',
            className: 'header-github-link',
            'aria-label': 'GitHub',
          },
          {
            href: 'https://www.linkedin.com/in/barisbayrak/',
            position: 'right',
            className: 'header-linkedin-link',
            'aria-label': 'LinkedIn',
          },
          {
            href: 'https://x.com/bbarisbayrak',
            position: 'right',
            className: 'header-x-link',
            'aria-label': 'X',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Connect',
            items: [
              {label: 'GitHub', href: 'https://github.com/brsbyrk'},
              {label: 'LinkedIn', href: 'https://www.linkedin.com/in/barisbayrak/'},
              {label: 'X', href: 'https://x.com/bbarisbayrak'},
            ],
          },
          {
            title: 'Content',
            items: [
              {label: 'Blog', to: '/blog'},
              {label: 'About', to: '/about'},
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
