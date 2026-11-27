import { posts, pages, postUrl, categories } from '../lib/data.js';
import eventsData from '../data/events.json';

const esc = (s = '') => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const day = (d) => (d || '').slice(0, 10);

export function GET({ site }) {
  const abs = (u) => new URL(u, site).href;
  const newest = posts[0] ? day(posts[0].modified || posts[0].date) : undefined;
  const entries = [];
  const add = (loc, lastmod, extra = '') => entries.push(`<url><loc>${esc(abs(loc))}</loc>${lastmod ? `<lastmod>${lastmod}</lastmod>` : ''}${extra}</url>`);

  add('/', newest);
  add('/jobs/', newest);
  add('/events/', day(eventsData.updated));
  add('/category/news/', newest);
  for (const p of pages) add(`/${p.slug}/`, day(p.modified));
  const cats = new Set([...categories.map((c) => c.slug), ...posts.flatMap((p) => p.categories)]);
  for (const c of cats) {
    if (c === 'news') continue;
    const list = posts.filter((p) => p.categories.includes(c));
    if (list.length) add(`/category/${c}/`, day(list[0].modified || list[0].date));
  }
  const tagCount = {};
  posts.forEach((p) => (p.tags || []).forEach((t) => { (tagCount[t] ||= []).push(p); }));
  for (const [t, list] of Object.entries(tagCount)) if (list.length >= 2) add(`/tag/${t}/`, day(list[0].modified || list[0].date));
  for (const p of posts) {
    const img = p.image?.src ? `<image:image><image:loc>${esc(abs(p.image.src))}</image:loc></image:image>` : '';
    add(postUrl(p), day(p.modified || p.date), img);
  }
  const seen = new Set();
  const unique = entries.filter((e) => { const k = e.match(/<loc>(.*?)<\/loc>/)[1]; if (seen.has(k)) return false; seen.add(k); return true; });
  return new Response(
    `<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">${unique.join('')}</urlset>`,
    { headers: { 'Content-Type': 'application/xml; charset=utf-8' } },
  );
}
