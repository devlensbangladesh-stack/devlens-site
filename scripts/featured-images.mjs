// Fills in each story's cover image from the old WordPress.com site (REST v1.1), then mirror-media copies it locally.
import fs from 'node:fs/promises';
import path from 'node:path';
const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const res = await fetch('https://public-api.wordpress.com/rest/v1.1/sites/215558473/posts/?number=100&fields=slug,title,featured_image,post_thumbnail');
if (!res.ok) throw new Error('HTTP ' + res.status);
const { posts } = await res.json();
let n = 0;
for (const p of posts) {
  const f = path.join(root, 'src/data/posts', `${p.slug}.json`);
  let d; try { d = JSON.parse(await fs.readFile(f, 'utf8')); } catch { continue; }
  const src = p.post_thumbnail?.URL || p.featured_image;
  if (!src || (d.image && d.image.src)) continue;
  d.image = { src: src.replace(/\?.*$/, ''), alt: `AI-generated illustration for the story: ${d.title}`, width: p.post_thumbnail?.width, height: p.post_thumbnail?.height };
  await fs.writeFile(f, JSON.stringify(d, null, 1)); n++;
}
console.log(`Cover images added to ${n} stories.`);
