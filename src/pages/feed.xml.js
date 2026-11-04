import { posts, postUrl } from '../lib/data.js';
const esc = (s = '') => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
export function GET({ site }) {
  const items = posts.slice(0, 30).map((p) => `<item><title>${esc(p.title)}</title><link>${new URL(postUrl(p), site)}</link><guid>${new URL(postUrl(p), site)}</guid><pubDate>${new Date(p.date + '+06:00').toUTCString()}</pubDate><description>${esc(p.excerpt)}</description></item>`).join('');
  return new Response(`<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Devlens Bangladesh</title><link>${site}</link><description>Development intelligence for Bangladesh</description>${items}</channel></rss>`, { headers: { 'Content-Type': 'application/rss+xml; charset=utf-8' } });
}
