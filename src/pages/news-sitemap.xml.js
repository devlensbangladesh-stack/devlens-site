import { posts, postUrl } from '../lib/data.js';

// Google News sitemap: stories published in the last two days.
const esc = (s = '') => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&apos;');
export function GET({ site }) {
  const cutoff = Date.now() - 2 * 86400000;
  let recent = posts.filter((p) => Date.parse(p.date + '+06:00') >= cutoff);
  if (!recent.length) recent = posts.slice(0, 10);
  const items = recent.slice(0, 1000).map((p) => `<url><loc>${esc(new URL(postUrl(p), site).href)}</loc><news:news><news:publication><news:name>Devlens Bangladesh</news:name><news:language>en</news:language></news:publication><news:publication_date>${p.date}+06:00</news:publication_date><news:title>${esc(p.title)}</news:title></news:news></url>`).join('');
  return new Response(`<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">${items}</urlset>`, { headers: { 'Content-Type': 'application/xml; charset=utf-8' } });
}
