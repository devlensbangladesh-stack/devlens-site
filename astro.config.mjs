import { defineConfig } from 'astro/config';

export default defineConfig({
  site: process.env.SITE_URL || 'https://devlensbd.pages.dev',
  trailingSlash: 'always',
  build: { format: 'directory' },
});
