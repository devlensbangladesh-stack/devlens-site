import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://devlensbd.org',
  trailingSlash: 'always',
  build: { format: 'directory' },
});
