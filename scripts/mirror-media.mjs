// Copies images still hosted on WordPress.com into public/media and points the site data at the local copy.
// Safe to run many times. Run with: node scripts/mirror-media.mjs
import fs from 'node:fs/promises';
import path from 'node:path';

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const RE = /https?:\/\/(?:i[0-3]\.wp\.com\/)?devlensbangladesh\.(?:files\.)?wordpress\.com\/(?:wp-content\/uploads\/)?(\d{4}\/\d{2}\/[A-Za-z0-9._-]+\.(?:jpe?g|png|gif|webp|svg))(?:\?[^"'\s)]*)?/g;

async function walk(dir) {
  const out = [];
  for (const e of await fs.readdir(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) out.push(...(await walk(p)));
    else if (/\.(json|astro|md)$/.test(e.name)) out.push(p);
  }
  return out;
}

const files = [...(await walk(path.join(root, 'src')))];
let downloaded = 0, failed = 0;
for (const f of files) {
  let text = await fs.readFile(f, 'utf8');
  const found = [...text.matchAll(RE)];
  if (!found.length) continue;
  for (const m of found) {
    const rel = m[1];
    const dest = path.join(root, 'public/media', rel);
    try { await fs.access(dest); } catch {
      const res = await fetch(`https://devlensbangladesh.wordpress.com/wp-content/uploads/${rel}`);
      if (!res.ok) { console.warn('Could not download', rel, res.status); failed++; continue; }
      await fs.mkdir(path.dirname(dest), { recursive: true });
      await fs.writeFile(dest, Buffer.from(await res.arrayBuffer()));
      downloaded++;
    }
    text = text.replaceAll(m[0], `/media/${rel}`);
  }
  text = text.replace(/\s(srcset|sizes)=\\?"[^"]*?\\?"/g, '');
  await fs.writeFile(f, text);
}
console.log(`Media mirror: ${downloaded} downloaded, ${failed} failed.`);
