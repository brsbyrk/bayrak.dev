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

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: false,
        blog: {
          routeBasePath: '/',
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
