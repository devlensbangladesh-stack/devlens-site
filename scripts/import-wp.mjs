// One-time import of all content from the old WordPress.com site into src/data.
// Run with: node scripts/import-wp.mjs   (needs internet access to public-api.wordpress.com)
import fs from 'node:fs/promises';
import path from 'node:path';

const SITE = '215558473';
const API = `https://public-api.wordpress.com/wp/v2/sites/${SITE}`;
const OLD = 'https://devlensbangladesh.wordpress.com';
const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');

async function getAll(endpoint, extra = '') {
  const out = [];
  for (let page = 1; ; page++) {
    const res = await fetch(`${API}/${endpoint}?per_page=100&page=${page}${extra}`);
    if (res.status === 400) break; // past the last page
    if (!res.ok) throw new Error(`${endpoint} page ${page}: HTTP ${res.status}`);
    const items = await res.json();
    out.push(...items);
    if (items.length < 100) break;
  }
  return out;
}

const decode = (s = '') =>
  s.replace(/&#8217;|&#039;|&#39;/g, "'").replace(/&#8216;/g, "'").replace(/&#8220;|&#8221;|&quot;/g, '"')
   .replace(/&#8211;/g, '-').replace(/&#8212;/g, ', ').replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&')
   .replace(/&hellip;|&#8230;/g, '...').replace(/<[^>]+>/g, '').trim();

const localLinks = (html = '') =>
  html.replaceAll(`${OLD}/wp-content/uploads/`, '@@MEDIA@@')
      .replaceAll(`${OLD}/`, '/')
      .replace(new RegExp(`href="${OLD}"`, 'g'), 'href="/"')
      .replaceAll('@@MEDIA@@', `${OLD}/wp-content/uploads/`);

async function main() {
  const [cats, tags, posts, pages] = await Promise.all([
    getAll('categories'), getAll('tags'), getAll('posts', '&status=publish'), getAll('pages', '&status=publish'),
  ]);
  const catSlug = Object.fromEntries(cats.map((c) => [c.id, c.slug]));
  const tagSlug = Object.fromEntries(tags.map((t) => [t.id, t.slug]));

  await fs.writeFile(path.join(root, 'src/data/categories.json'),
    JSON.stringify(cats.map((c) => ({ slug: c.slug, name: decode(c.name), description: decode(c.description) })), null, 1));
  await fs.writeFile(path.join(root, 'src/data/tags.json'),
    JSON.stringify(tags.map((t) => ({ slug: t.slug, name: decode(t.name), description: decode(t.description) })), null, 1));

  const mediaIds = [...new Set(posts.map((p) => p.featured_media).filter(Boolean))];
  const media = {};
  for (const id of mediaIds) {
    const r = await fetch(`${API}/media/${id}`);
    if (r.ok) { const m = await r.json(); media[id] = { src: m.source_url, alt: m.alt_text || '', width: m.media_details?.width, height: m.media_details?.height }; }
  }

  for (const p of posts) {
    const post = {
      slug: p.slug, date: p.date, modified: p.modified,
      title: decode(p.title.rendered), excerpt: decode(p.excerpt.rendered),
      categories: p.categories.map((id) => catSlug[id]).filter(Boolean),
      tags: p.tags.map((id) => tagSlug[id]).filter(Boolean),
      image: media[p.featured_media] || null,
      content: localLinks(p.content.rendered),
    };
    await fs.writeFile(path.join(root, 'src/data/posts', `${p.slug}.json`), JSON.stringify(post, null, 1));
  }
  for (const p of pages) {
    if (['home', 'jobs'].includes(p.slug)) continue; // rebuilt as code
    await fs.writeFile(path.join(root, 'src/data/pages', `${p.slug}.json`),
      JSON.stringify({ slug: p.slug, title: decode(p.title.rendered), excerpt: decode(p.excerpt.rendered), content: localLinks(p.content.rendered) }, null, 1));
  }
  console.log(`Imported ${posts.length} posts, ${pages.length} pages, ${cats.length} categories, ${tags.length} tags.`);
}
main().catch((e) => { console.error(e); process.exit(1); });
