import { posts, pages, postUrl } from '../lib/data.js';
export function GET({ site }) {
  const urls = ['/', '/jobs/', ...pages.map((p) => `/${p.slug}/`), ...posts.map(postUrl)];
  return new Response(`<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${urls.map((u) => `<url><loc>${new URL(u, site)}</loc></url>`).join('')}</urlset>`, { headers: { 'Content-Type': 'application/xml' } });
}
